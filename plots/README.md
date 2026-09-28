# `plots/` — CSV → seaborn PDF plots

Deterministic conversion of aggregated study CSVs into publication-ready
matplotlib/seaborn plots for the thesis. Each plot is written to
`plots/<name>.pdf` and is intended to be included via
`\includegraphics[width=\linewidth]{plots/<name>.pdf}` inside a `figure`
float in the thesis (caption below, per LaTeX figure convention).

Every generated file records provenance in its PDF metadata `/Subject`:
`AUTO-GENERATED from <source> -- do not edit by hand.` `/CreationDate` is
pinned so re-running the build is byte-stable.

## Regenerate all plots

```bash
uv run python -m plots.build
```

Exits non-zero on any error.

## Add a new plot

1. Drop the source CSV somewhere in the repo (usually under `study/…`).
2. Create `plots/specs/<name>.yaml`:

   ```yaml
   name: my_plot
   kind: small_multiples_line
   source: path/relative/to/repo/root.csv
   filter:
     allow:
       source: [models]
       model: [gpt-5.4-mini, gpt-5.4]
   x:
     column: prompt_key
     order: [poor, medium, rich]
     label: Prompt richness
   y:
     column: hm_f1
     label: Macro F1
     limit: [0.0, 1.0]
   hue:
     column: model
     title: Model
   facet:
     column: case_id
     title_template: "Case {value}"
   aggregate:
     by: [case_id, model, prompt_key]
     method: mean
     errorbar: sd
     dodge: 0.4
   figure:
     figsize: [7.0, 2.6]
     legend: right
   ```

3. Run `uv run python -m plots.build`. It writes `plots/my_plot.pdf`.
4. In the thesis, include with `\includegraphics[width=\linewidth]{plots/my_plot.pdf}` inside a `figure` float.

## Spec reference

| Field                                       | Type                | Notes                                                            |
| ------------------------------------------- | ------------------- | ---------------------------------------------------------------- |
| `name`                                      | str                 | Output filename stem (`plots/<name>.pdf`)                        |
| `kind`                                      | str                 | Renderer key. Supported: `small_multiples_line`, `grouped_bar`   |
| `source`                                    | path                | CSV relative to repo root                                        |
| `filter.allow`                              | `{col: [values]}`   | Row allowlist per column (AND across columns)                    |
| `x.column` / `order` / `label`              | str / list / str    | Categorical x-axis                                               |
| `y.column` / `label` / `limit`              | str / str / [lo,hi] | Continuous y-axis; y-limit shared across facets                  |
| `hue.column` / `order` / `title`            | str / list / str    | Series grouping; drives legend                                   |
| `facet.column` / `order` / `title_template` | str / list / str    | Small-multiples facet; `title_template` receives `{value}`       |
| `facet.labels`                              | `{value: label}`    | Optional explicit panel titles; overrides `title_template`       |
| `hue.labels`                                | `{value: label}`    | Optional explicit legend labels (parallels `facet.labels`)       |
| `aggregate.by`                              | list                | Grouping columns for the mean line                               |
| `aggregate.errorbar`                        | str                 | Variance indicator: `sd` (+/-1 std) or `none`                    |
| `aggregate.dodge`                           | float               | Horizontal offset between hue groups at each x tick (0 disables) |
| `figure.figsize`                            | [w, h]              | Inches                                                           |
| `figure.legend`                             | str                 | `right` (only value currently supported)                         |

## Style

All colors, sizes, and stroke widths live in `plots/style.py`. Renderers
must not define their own. Series colors come from seaborn's `colorblind`
palette; structural chrome (facet titles, annotative tints) uses the
`LAYER_ACCENTS` palette ported from `thesis/diagrams/_lib/style.typ`.

`tests/plots/test_palette_consistency.py` catches drift between the
Python constants here and the typst file in the sibling `thesis/` repo.
It skips gracefully if the thesis repo is not present.

## Preprocessed data dependencies

Some specs read a preprocessed CSV built by a script in `study/preprocessed/`.
Rerun the corresponding builder whenever `sessions.csv` or a source in
`study/preprocessed/` changes:

- `perfield_case_gpt54` reads `study/preprocessed/eval_perfield_case_gpt54_long.csv`,
  produced by `uv run python -m study.preprocessed.build_eval_perfield_case_gpt54`
  (joins `hashmatch_fields.csv` with `sessions.csv`; rerun after either changes).

## Tests

```bash
uv run pytest tests/plots/
```
