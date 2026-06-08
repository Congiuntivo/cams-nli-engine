from __future__ import annotations

from nli_engine.engine.llm import LLMClient
from nli_engine.engine.prompts import load_prompt
from nli_engine.engine.retrieval.backends.qdrant import QdrantRetriever
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
from nli_engine.engine.workflow.assembly import AssemblyPlan
from nli_engine.engine.workflow.base import Message, Workflow, WorkflowContext
from nli_engine.engine.workflow.config import WorkflowConfig
from nli_engine.engine.workflow.result import TurnResult
from nli_engine.engine.workflow.specialist import build_specialist_tool
from nli_engine.engine.workflow.steps.extraction import ExtractionStep
from nli_engine.engine.workflow.steps.llm import LLMStep


def _load_prompt(filename: str) -> str:
    return load_prompt("nli_engine.engine.prompts.one_shot", filename)


def _load_specialist_prompt(filename: str) -> str:
    return load_prompt("nli_engine.engine.prompts.one_shot.specialists", filename)


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

        refiner_client = LLMClient(
            model=config.models.get("refiner", config.models["default"])
        )
        self._refinement_step = LLMStep(
            name="refiner",
            client=refiner_client,
            system_prompt=_load_prompt("refiner.md"),
            max_iterations=config.max_iterations.get("refiner", 3),
            retriever=self._retriever,
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
        )

        for tool in self._build_specialist_steps(
            specialist_client, config, self._retriever
        ):
            self._all_tools[tool.name] = tool

        orchestrator_client = LLMClient(
            model=config.models.get("orchestrator", config.models["default"])
        )
        self._orchestrator_step = LLMStep(
            name="orchestrator",
            tool_names=UNIT_SPECIALIST_NAMES,
            client=orchestrator_client,
            system_prompt=_load_prompt("orchestrator.md"),
            max_iterations=config.max_iterations.get("orchestrator", 20),
            retriever=self._retriever,
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

        return [
            build_specialist_tool(
                name="device_specialist",
                description=(
                    "Create a connected device (eSense, Movesense, Movisens, "
                    "Polar) or service (location, weather, air quality, health). "
                    "Call once per Assembly Unit when a connected device is needed."
                ),
                step=LLMStep(
                    name="device_specialist",
                    client=client,
                    system_prompt=_load_specialist_prompt("device.md"),
                    max_iterations=max_iter.get("device_specialist", 5),
                    retriever=retriever,
                ),
                domain_tools=self._tools_for_names(DEVICE_SPECIALIST_TOOL_NAMES),
            ),
            build_specialist_tool(
                name="trigger_specialist",
                description=(
                    "Create a trigger (immediate, delayed, periodic, cron, "
                    "manual, or no_op). Call once per Assembly Unit."
                ),
                step=LLMStep(
                    name="trigger_specialist",
                    client=client,
                    system_prompt=_load_specialist_prompt("trigger.md"),
                    max_iterations=max_iter.get("trigger_specialist", 5),
                    retriever=retriever,
                ),
                domain_tools=self._tools_for_names(TRIGGER_SPECIALIST_TOOL_NAMES),
            ),
            build_specialist_tool(
                name="task_specialist",
                description=(
                    "Create a task (background, app, health_app, or web). "
                    "Call once per Assembly Unit."
                ),
                step=LLMStep(
                    name="task_specialist",
                    client=client,
                    system_prompt=_load_specialist_prompt("task.md"),
                    max_iterations=max_iter.get("task_specialist", 5),
                    retriever=retriever,
                ),
                domain_tools=self._tools_for_names(TASK_SPECIALIST_TOOL_NAMES),
            ),
            build_specialist_tool(
                name="task_control_assembler",
                description=(
                    "Bind a trigger, a task, and a device role into a TaskControl. "
                    "Call last within each Assembly Unit, after all prerequisites exist."
                ),
                step=LLMStep(
                    name="task_control_assembler",
                    client=client,
                    system_prompt=_load_specialist_prompt("task_control.md"),
                    max_iterations=max_iter.get("task_control_assembler", 5),
                    retriever=retriever,
                ),
                domain_tools=self._tools_for_names(TASK_CONTROL_ASSEMBLER_TOOL_NAMES),
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
        _, log = self._setup_step.run(
            context, self._tools_for_names(SETUP_SPECIALIST_TOOL_NAMES)
        )
        logs.append(log)
        if stop_after == "setup":
            return TurnResult(message="", logs=logs, done=True)

        # One orchestrator invocation per assembly unit. The shared context
        # carries full history across units so AU N+1 sees AU N's work.
        n = len(assembly_plan.units)
        final_text = ""
        for i, unit in enumerate(assembly_plan.units):
            context.history.append(
                Message(
                    role="user",
                    content=f"Assemble assembly unit {i + 1} of {n}: {unit.description}",
                )
            )
            final_text, log = self._orchestrator_step.run(
                context,
                self._resolve_tools(self._orchestrator_step),
            )
            logs.append(log)

        protocol = self._session.serialize()
        return TurnResult(
            message=final_text,
            logs=logs,
            done=True,
            protocol=protocol,
        )
