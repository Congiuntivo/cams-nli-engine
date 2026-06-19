from __future__ import annotations

from nli_engine.engine.llm import LLMClient
from nli_engine.engine.prompts import load_prompt
from nli_engine.engine.retrieval.backends.qdrant import QdrantRetriever
from nli_engine.engine.retrieval.query import LLMQueryRewriter, QueryExtractor
from nli_engine.engine.retrieval.retriever import Retriever
from nli_engine.engine.session import ProtocolSession
from nli_engine.engine.tools import BoundTool
from nli_engine.engine.tools.registry import (
    DEVICE_SPECIALIST_TOOL_NAMES,
    SETUP_SPECIALIST_TOOL_NAMES,
    TASK_CONTROL_ASSEMBLER_TOOL_NAMES,
    TASK_SPECIALIST_TOOL_NAMES,
    TRIGGER_SPECIALIST_TOOL_NAMES,
    UNIT_SPECIALIST_NAMES,
)
from nli_engine.engine.workflow.assembly import AssemblyPlan, OrchestratorResult
from nli_engine.engine.workflow.base import Message, Workflow, WorkflowContext
from nli_engine.engine.workflow.config import WorkflowConfig
from nli_engine.engine.workflow.result import TurnResult
from nli_engine.engine.workflow.retrieval_tool import build_retrieve_docs_tool
from nli_engine.engine.workflow.specialist import build_specialist_tool
from nli_engine.engine.workflow.steps.extraction import ExtractionStep
from nli_engine.engine.workflow.steps.llm import LLMStep

_RETRIEVE_DOCS_TOOL_NAME = "retrieve_docs"


def _load_prompt(filename: str) -> str:
    return load_prompt("nli_engine.engine.prompts.one_shot", filename)


def _load_specialist_prompt(filename: str) -> str:
    return load_prompt("nli_engine.engine.prompts.one_shot.specialists", filename)


_SPECIALIST_PROMPT_BY_NAME: dict[str, str] = {
    "device_specialist": "device.md",
    "trigger_specialist": "trigger.md",
    "task_specialist": "task.md",
    "task_control_assembler": "task_control.md",
}


class OneShotLLMWorkflowContext(WorkflowContext):
    """Workflow context for OneShotLLMWorkflow."""


class OneShotLLMWorkflow(Workflow[OneShotLLMWorkflowContext]):
    """Five-step LLM workflow: refiner → planner → extractor → setup → orchestrator loop.

    The refiner rewrites the raw user message into a clean, unambiguous natural
    language description. The planner produces a concise ordered action plan.
    The extractor parses that plan into a structured ``AssemblyPlan``. Python
    then drives the assembly: the setup step runs once against the shared context,
    and the orchestrator is invoked once per assembly unit, delegating to domain
    specialists — device, trigger, task, and task_control_assembler.

    Required model keys in WorkflowConfig:

    - ``models["refiner"]``: model for the refiner step.
    - ``models["planner"]``: model for the planner step.
    - ``models["extractor"]``: model for the extraction step.
    - ``models["orchestrator"]``: model for the orchestrator step.
    - ``models["specialist"]``: shared model for all specialist steps.

    Optional model keys:

    - ``models["query_rewriter"]``: small/cheap model for the LLM-based
      retrieval query rewriter. Falls back to ``models["default"]`` when absent.

    """

    def __init__(self, config: WorkflowConfig, session: ProtocolSession) -> None:
        """
        Args:
            config: Must contain ``models["refiner"]``, ``models["planner"]``,
                ``models["extractor"]``, ``models["orchestrator"]``, and
                ``models["specialist"]``.
            session: Live authoring session used to bind and dispatch tools.

        Raises:
            KeyError: If any required model key is absent from ``config.models``.
        """
        super().__init__(config, session)

        self._retriever: Retriever | None = None
        self._retrieval_top_k = 5
        self._retrieval_min_score = 0.0
        if config.retrieval is not None:
            rc = config.retrieval
            self._retriever = QdrantRetriever(
                dense_model=rc.dense_model,
                sparse_model=rc.sparse_model,
                multi_model=rc.multi_model,
                method=rc.method,
                rerank=rc.rerank,
                prefetch_limit=rc.prefetch_limit,
            )
            self._retrieval_top_k = rc.top_k
            self._retrieval_min_score = rc.min_score

        # Shared LLM-based query rewriter. Used by every step that has a
        # retriever so each step gets a focused query tailored to its current
        # context instead of the raw multi-topic user message.
        self._query_rewriter: QueryExtractor | None = None
        if self._retriever is not None:
            rewriter_client = LLMClient(
                model=config.models.get("query_rewriter", config.models["default"])
            )
            self._query_rewriter = LLMQueryRewriter(
                client=rewriter_client,
                system_prompt=_load_prompt("query_rewriter.md"),
            )

            # On-demand retrieval tool exposed to multi-iteration steps so the
            # model can refresh its context after the warm injection at
            # iteration 0 goes stale.
            self._all_tools[_RETRIEVE_DOCS_TOOL_NAME] = build_retrieve_docs_tool(
                retriever=self._retriever,
                top_k=self._retrieval_top_k,
                min_score=self._retrieval_min_score,
            )

        refiner_client = LLMClient(
            model=config.models.get("refiner", config.models["default"])
        )
        self._refinement_step = LLMStep(
            name="refiner",
            client=refiner_client,
            system_prompt=_load_prompt("refiner.md"),
            max_iterations=config.max_iterations.get("refiner", 3),
        )

        planner_client = LLMClient(
            model=config.models.get("planner", config.models["default"])
        )
        self._planning_step = LLMStep(
            name="planner",
            client=planner_client,
            system_prompt=_load_prompt("planner.md"),
            max_iterations=config.max_iterations.get("planner", 1),
            retriever=self._retriever,
            query_extractor=self._query_rewriter,
            top_k=self._retrieval_top_k,
            min_score=self._retrieval_min_score,
        )

        extractor_client = LLMClient(
            model=config.models.get("extractor", config.models["default"])
        )
        self._extraction_step: ExtractionStep[AssemblyPlan] = ExtractionStep(
            name="extractor",
            client=extractor_client,
            system_prompt=_load_prompt("assembly_plan_extraction.md"),
            schema=AssemblyPlan,
        )

        specialist_client = LLMClient(
            model=config.models.get("specialist", config.models["default"])
        )
        self._setup_step = LLMStep(
            name="setup_specialist",
            client=specialist_client,
            system_prompt=_load_specialist_prompt("setup.md"),
            max_iterations=config.max_iterations.get("setup_specialist", 5),
            retriever=self._retriever,
            query_extractor=self._query_rewriter,
            top_k=self._retrieval_top_k,
            min_score=self._retrieval_min_score,
        )

        for tool in self._build_specialist_steps(
            specialist_client, config, self._retriever
        ):
            self._all_tools[tool.name] = tool

        orchestrator_client = LLMClient(
            model=config.models.get("orchestrator", config.models["default"])
        )
        orchestrator_tools = list(UNIT_SPECIALIST_NAMES)
        if self._retriever is not None:
            orchestrator_tools.append(_RETRIEVE_DOCS_TOOL_NAME)
        self._orchestrator_step = LLMStep(
            name="orchestrator",
            tool_names=orchestrator_tools,
            client=orchestrator_client,
            system_prompt=_load_prompt("orchestrator.md"),
            max_iterations=config.max_iterations.get("orchestrator", 20),
            retriever=self._retriever,
            query_extractor=self._query_rewriter,
            top_k=self._retrieval_top_k,
            min_score=self._retrieval_min_score,
        )
        self._orchestrator_result_step: ExtractionStep[OrchestratorResult] = (
            ExtractionStep(
                name="orchestrator_result",
                client=orchestrator_client,
                system_prompt=_load_prompt("orchestrator_result_extraction.md"),
                schema=OrchestratorResult,
            )
        )

    def _tools_for_names(self, names: list[str]) -> list[BoundTool]:
        """Return the BoundTools for a given list of tool names.

        Args:
            names: Tool names to resolve from the session's tool map.

        Returns:
            Ordered list of BoundTools matching the requested names.

        Raises:
            ValueError: If any name is absent from the session tool map.
        """
        missing = [n for n in names if n not in self._all_tools]
        if missing:
            raise ValueError(f"Unknown tool names: {missing}")
        return [self._all_tools[n] for n in names]

    def _build_specialist_steps(
        self,
        client: LLMClient,
        config: WorkflowConfig,
        retriever: Retriever | None,
    ) -> list[BoundTool]:
        """Construct the four per-unit specialist delegation tools.

        Each specialist is an LLMStep wrapped as a BoundTool so the orchestrator
        can call it via standard tool calling with a DelegationRequest.

        Args:
            client: Shared LLMClient for all specialist steps.
            config: WorkflowConfig for per-specialist max_iterations overrides.
            retriever: Optional retrieval backend passed to each specialist step.
                When ``None``, specialists run without retrieval.

        Returns:
            List of four BoundTools in canonical order: device, trigger, task,
            task_control_assembler.
        """
        max_iter = config.max_iterations
        # When retrieval is configured, expose the on-demand retrieve_docs tool
        # alongside each specialist's domain tools so high-iteration specialists
        # can refresh their context as the conversation evolves.
        retrieve_docs_extras: list[BoundTool] = (
            [self._all_tools[_RETRIEVE_DOCS_TOOL_NAME]] if retriever is not None else []
        )

        def _make_step(name: str) -> LLMStep:
            return LLMStep(
                name=name,
                client=client,
                system_prompt=_load_specialist_prompt(_SPECIALIST_PROMPT_BY_NAME[name]),
                max_iterations=max_iter.get(name, 5),
                retriever=retriever,
                query_extractor=self._query_rewriter,
                top_k=self._retrieval_top_k,
                min_score=self._retrieval_min_score,
            )

        return [
            build_specialist_tool(
                name="device_specialist",
                description=(
                    "Create a connected device (eSense, Movesense, Movisens, "
                    "Polar) or service (location, weather, air quality, health). "
                    "Call once per Assembly Unit when a connected device is needed."
                ),
                step=_make_step("device_specialist"),
                domain_tools=self._tools_for_names(DEVICE_SPECIALIST_TOOL_NAMES)
                + retrieve_docs_extras,
            ),
            build_specialist_tool(
                name="trigger_specialist",
                description=(
                    "Create a trigger (immediate, delayed, periodic, cron, "
                    "manual, or no_op). Call once per Assembly Unit."
                ),
                step=_make_step("trigger_specialist"),
                domain_tools=self._tools_for_names(TRIGGER_SPECIALIST_TOOL_NAMES)
                + retrieve_docs_extras,
            ),
            build_specialist_tool(
                name="task_specialist",
                description=(
                    "Create a task (background, app, health_app, or web). "
                    "Call once per Assembly Unit."
                ),
                step=_make_step("task_specialist"),
                domain_tools=self._tools_for_names(TASK_SPECIALIST_TOOL_NAMES)
                + retrieve_docs_extras,
            ),
            build_specialist_tool(
                name="task_control_assembler",
                description=(
                    "Bind a trigger, a task, and a device role into a TaskControl. "
                    "Call last within each Assembly Unit, after all prerequisites exist."
                ),
                step=_make_step("task_control_assembler"),
                domain_tools=self._tools_for_names(TASK_CONTROL_ASSEMBLER_TOOL_NAMES)
                + retrieve_docs_extras,
            ),
        ]

    def run_turn(
        self, user_input: str, context: OneShotLLMWorkflowContext
    ) -> TurnResult:
        """Run one user turn through the full pipeline.

        Steps in order:
        1. Refiner rewrites the raw user message.
        2. Planner produces an ordered assembly plan.
        3. Extractor parses the plan into a structured ``AssemblyPlan`` (not
           appended to history).
        4. Setup step runs once against the shared context, creating shared
           infrastructure and appending its full exchange to history.
        5. For each assembly unit, the orchestrator is invoked once and delegates
           to the four per-unit specialists. All invocations share the same
           context so each one sees the full history of prior units.

        Args:
            user_input: Raw free-text instruction from the user.
            context: Mutable workflow state shared across all steps.

        Returns:
            TurnResult with ``done=True``, the final orchestrator text, and
            the serialised protocol dict.
        """
        context.history.append(Message(role="user", content=user_input))

        logs = []
        stop_after = self.config.parameters.get("stop_after")

        refiner_text, log = self._refinement_step.run(context)
        logs.append(log)
        if stop_after == "refiner":
            return TurnResult(message=refiner_text, logs=logs, done=True)

        planner_text, log = self._planning_step.run(context)
        logs.append(log)
        if stop_after == "planner":
            return TurnResult(message=planner_text, logs=logs, done=True)

        assembly_plan, log = self._extraction_step.run(
            context=OneShotLLMWorkflowContext(history=context.history[-1:]), tools=[]
        )
        logs.append(log)
        if stop_after == "extractor":
            return TurnResult(
                message=assembly_plan.model_dump_json(indent=2), logs=logs, done=True
            )

        # Setup runs once as a plain step: its tool calls and result are appended
        # to the shared history, giving every subsequent orchestrator invocation
        # full visibility into what was created.
        setup_tools = self._tools_for_names(SETUP_SPECIALIST_TOOL_NAMES)
        if self._retriever is not None:
            setup_tools = setup_tools + [self._all_tools[_RETRIEVE_DOCS_TOOL_NAME]]
        _, log = self._setup_step.run(context, setup_tools)
        logs.append(log)
        if stop_after == "setup":
            return TurnResult(message="", logs=logs, done=True)

        # One orchestrator invocation per assembly unit. The shared context
        # carries full history across units so AU N+1 sees AU N's work.
        # Failed units are retried up to max_unit_retries times with error context
        # injected; residual failures are surfaced in TurnResult.partial_failures.
        max_unit_retries = self.config.parameters.get("max_unit_retries", 1)
        partial_failures: list[str] = []
        n = len(assembly_plan.units)
        final_text = ""
        orch_result = OrchestratorResult(success=True)

        for i, unit in enumerate(assembly_plan.units):
            context.history.append(
                Message(
                    role="user",
                    content=f"Assemble assembly unit {i + 1} of {n}: {unit.description}",
                )
            )

            for attempt in range(max_unit_retries + 1):
                if attempt > 0:
                    issues = "; ".join(orch_result.open_questions)
                    context.history.append(
                        Message(
                            role="user",
                            content=(
                                f"Assembly unit {i + 1} is incomplete. Issues: {issues}. "
                                "Retry, resolving the open questions above."
                            ),
                        )
                    )

                final_text, log = self._orchestrator_step.run(
                    context,
                    self._resolve_tools(self._orchestrator_step),
                )
                logs.append(log)

                extraction_context = OneShotLLMWorkflowContext(
                    history=[Message(role="user", content=final_text)]
                )
                orch_result, extraction_log = self._orchestrator_result_step.run(
                    extraction_context
                )
                logs.append(extraction_log)

                if orch_result.success:
                    break
            else:
                issues = "; ".join(orch_result.open_questions)
                partial_failures.append(f"Unit {i + 1} ({unit.name}): {issues}")

        protocol = self._session.serialize()
        return TurnResult(
            message=final_text,
            logs=logs,
            done=True,
            protocol=protocol,
            partial_failures=partial_failures,
        )
