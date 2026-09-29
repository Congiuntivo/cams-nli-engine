# `tables/` — CSV/JSON → LaTeX `tblr` fragments

Deterministic conversion of result CSVs/JSONs into LaTeX table fragments for the thesis. Each fragment is written to `tables/<name>.tex` and contains only the `\begin{tblr}...\end{tblr}` environment — the table float, `\caption`, `\label`, and `\centering` live in the document.

Every generated file starts with `% AUTO-GENERATED from <source> by tables/build.py — do not edit by hand.`

## Regenerate all tables

```bash
uv run python -m tables.build
```

Exits non-zero on any error. Output is byte-stable given the same inputs.

## Add a new table

1. Drop the source CSV or JSON somewhere in the repo (usually under `dataset/…` or `study/…`).
2. Create `tables/specs/<name>.yaml`:

   ```yaml
   name: my_table
   source: path/relative/to/repo/root.csv
   csv_options:
     comment: "#" # optional, skip header comment lines
   sort_by:
     - column: model
     - column: split
       order: [dev, test] # optional categorical order
   columns:
     - name: model
       header: Model
       type: text
     - name: accuracy
       header: Accuracy
       type: numeric
       decimals: 3
       highlight: max # optional: max | min
   spans: # optional spanning header groups
     - label: Overall
       columns: [accuracy, f1]
   row_group: # optional row grouping
     column: task
     style: cmidrule # cmidrule | label
   ```

3. Run `uv run python -m tables.build`. It writes `tables/my_table.tex`.
4. In the thesis, wrap with a table float and `\input{tables/my_table.tex}`.

## Preprocessed sources

Some tables consume a CSV that is itself derived from a larger raw source. In that
case, the preprocessing script lives with the raw data and must be rerun whenever
the raw source changes:

| Table                                           | Source CSV                                                                                             | Rebuild command                                                |
| ----------------------------------------------- | ------------------------------------------------------------------------------------------------------ | -------------------------------------------------------------- |
| `eval_quality`                                  | `study/preprocessed/eval_quality_wide.csv`                                                             | `uv run python -m study.preprocessed.build_eval_quality`       |
| `eval_perfield_tier`                            | `study/preprocessed/eval_perfield_tier_wide.csv`                                                       | `uv run python -m study.preprocessed.build_eval_perfield_tier` |
| `eval_baseline_summary` / `eval_baseline_cells` | `study/preprocessed/eval_baseline_summary_wide.csv`, `study/preprocessed/eval_baseline_cells_wide.csv` | `uv run python -m study.preprocessed.build_eval_baseline`      |
| `eval_execution`                                | `study/preprocessed/eval_execution_wide.csv`                                                           | `uv run python -m study.preprocessed.build_eval_execution`     |
| `eval_norag_summary` / `eval_norag_cells`       | `study/preprocessed/eval_norag_summary_wide.csv`, `study/preprocessed/eval_norag_cells_wide.csv`       | `uv run python -m study.preprocessed.build_eval_norag`         |

The `eval_quality` table depends on `study/preprocessed/eval_quality_wide.csv`,
produced from `study/preprocessed/sessions.csv`. Rerun the preprocessing script
before `tables.build` after `sessions.csv` changes.

The `eval_perfield_tier` table depends on
`study/preprocessed/eval_perfield_tier_wide.csv`, produced from
`study/preprocessed/hashmatch_fields.csv` joined against `sessions.csv`. Rerun
its preprocessor before `tables.build` after either source changes.

The `eval_baseline_summary` and `eval_baseline_cells` tables share a single
preprocessor that reads `study/preprocessed/sessions.csv`, filters to the
`gpt-5.4` pipeline arm (`source == "models"`) and the ReAct baseline arm
(`source == "react_baseline"`), and writes two wide CSVs. Rerun it before
`tables.build` after `sessions.csv` changes.

The `eval_execution` table depends on
`study/preprocessed/eval_execution_wide.csv`, produced from
`study/preprocessed/sessions.csv` (filtered to the five cloud pipeline models
under `source == "models"`, aggregated per `(model, case)` over the nine
richness × run sessions). Rerun its preprocessor before `tables.build` after
`sessions.csv` changes.

The `eval_norag_summary` and `eval_norag_cells` tables share a single
preprocessor that reads `study/preprocessed/sessions.csv`, filters to the
with-RAG arm (`source == "models" AND model == "gpt-5.4"`) and the no-RAG
ablation arm (`source == "norag"`), and writes two wide CSVs. Rerun it
before `tables.build` after `sessions.csv` changes.

## Spec reference

| Field                    | Type                         | Notes                                                                                                                                                                                                                                                                                          |
| ------------------------ | ---------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `name`                   | str                          | Output filename stem                                                                                                                                                                                                                                                                           |
| `source`                 | path                         | CSV or JSON, relative to repo root                                                                                                                                                                                                                                                             |
| `csv_options.comment`    | str                          | Skip lines starting with this char                                                                                                                                                                                                                                                             |
| `sort_by[]`              | list                         | `{column, order?}`; applied stably in listed order                                                                                                                                                                                                                                             |
| `columns[]`              | list                         | Ordered ColumnSpec list                                                                                                                                                                                                                                                                        |
| `columns[].name`         | str                          | Source column name                                                                                                                                                                                                                                                                             |
| `columns[].header`       | str                          | Display header (LaTeX special chars are escaped)                                                                                                                                                                                                                                               |
| `columns[].type`         | `text` \| `numeric` \| `raw` | Determines colspec (`l`/`X` vs `S[…]` vs `c`). `raw` cells are emitted verbatim (no escape, no formatting, no highlight) — use for pre-formatted LaTeX content that does not fit the `S` column contract (e.g. rows with per-row decimals).                                                    |
| `columns[].decimals`     | int                          | Fixed decimals for numeric printing                                                                                                                                                                                                                                                            |
| `columns[].table_format` | str                          | siunitx `table-format`; inferred from data if omitted                                                                                                                                                                                                                                          |
| `columns[].wrap`         | bool                         | Text only: use `X` instead of `l`                                                                                                                                                                                                                                                              |
| `columns[].highlight`    | `max` \| `min`               | Bold the extremum in this column; ties all bolded. `max` never bolds a value of exactly `0.0` (avoids highlighting `0.000 ± 0.000` cells as the winner).                                                                                                                                       |
| `columns[].sd_column`    | str                          | Numeric only. Pair with another column carrying the standard deviation; cell renders as `mean \pm sd`. Highlight compares on the mean alone.                                                                                                                                                   |
| `spans[]`                | list                         | `{label, columns[]}`; columns must be contiguous                                                                                                                                                                                                                                               |
| `row_group`              | obj                          | `{column, style}`; break on value change                                                                                                                                                                                                                                                       |
| `sections`               | str                          | Column name. Partitions rows by that column's value and emits one `tblr` block per section, separated by `\vspace{0.5em}`. Each block adds a spanning header carrying the section value over every column except the first. Highlights compute per-block. The sections column is not rendered. |

## LaTeX document requirements

Load these in the thesis preamble:

```latex
\usepackage{booktabs}
\usepackage{siunitx}
\sisetup{detect-weight=true, detect-family=true, mode=match}   % so \bfseries lands inside S columns
\usepackage{tabularray}
\UseTblrLibrary{siunitx}    % teach tblr about S[] columns
\UseTblrLibrary{booktabs}   % \toprule / \midrule / \cmidrule inside tblr
```

Without `\UseTblrLibrary{siunitx}` the fragments fail with `Unknown Column type S!`. Without `detect-weight` (and, for many font packages, `detect-family`) the `highlight: max` bolds render at the correct weight in the source but siunitx silently re-typesets the number in its regular font — the bold "does not land".

If any spec uses `sd_column` (paired mean ± sd cells), add `separate-uncertainty=true` to the same `\sisetup{}` call:

```latex
\sisetup{detect-weight=true, detect-family=true, mode=match, separate-uncertainty=true}
```

Cells are emitted as `{$X.YYY \pm Y.YYY$}` — the braces stop siunitx from
parsing the cell as a single number, and the inner `$...$` puts `\pm` in math
mode. `separate-uncertainty=true` keeps rendering consistent with any
hand-authored `\num{0.784(123)}` elsewhere in prose.

## JSON sources

`.json` sources are loaded as a flat list of objects (`[{col: val, ...}, ...]`). Nested normalization (`pandas.json_normalize`-style) is not implemented yet — add it when a spec needs it.

## Tests

```bash
uv run pytest tests/tables/
```

The snapshot test renders `tests/tables/fixtures/spec.yaml` and diffs against `tests/tables/fixtures/expected.tex`. Update the snapshot deliberately when renderer output changes.
