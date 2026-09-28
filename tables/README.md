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

| Table          | Source CSV                                 | Rebuild command                                          |
| -------------- | ------------------------------------------ | -------------------------------------------------------- |
| `eval_quality` | `study/preprocessed/eval_quality_wide.csv` | `uv run python -m study.preprocessed.build_eval_quality` |

The `eval_quality` table depends on `study/preprocessed/eval_quality_wide.csv`,
produced from `study/preprocessed/sessions.csv`. Rerun the preprocessing script
before `tables.build` after `sessions.csv` changes.

## Spec reference

| Field                    | Type                | Notes                                                 |
| ------------------------ | ------------------- | ----------------------------------------------------- |
| `name`                   | str                 | Output filename stem                                  |
| `source`                 | path                | CSV or JSON, relative to repo root                    |
| `csv_options.comment`    | str                 | Skip lines starting with this char                    |
| `sort_by[]`              | list                | `{column, order?}`; applied stably in listed order    |
| `columns[]`              | list                | Ordered ColumnSpec list                               |
| `columns[].name`         | str                 | Source column name                                    |
| `columns[].header`       | str                 | Display header (LaTeX special chars are escaped)      |
| `columns[].type`         | `text` \| `numeric` | Determines colspec (`l`/`X` vs `S[…]`)                |
| `columns[].decimals`     | int                 | Fixed decimals for numeric printing                   |
| `columns[].table_format` | str                 | siunitx `table-format`; inferred from data if omitted |
| `columns[].wrap`         | bool                | Text only: use `X` instead of `l`                     |
| `columns[].highlight`    | `max` \| `min`      | Bold the extremum in this column; ties all bolded     |
| `spans[]`                | list                | `{label, columns[]}`; columns must be contiguous      |
| `row_group`              | obj                 | `{column, style}`; break on value change              |

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

## JSON sources

`.json` sources are loaded as a flat list of objects (`[{col: val, ...}, ...]`). Nested normalization (`pandas.json_normalize`-style) is not implemented yet — add it when a spec needs it.

## Tests

```bash
uv run pytest tests/tables/
```

The snapshot test renders `tests/tables/fixtures/spec.yaml` and diffs against `tests/tables/fixtures/expected.tex`. Update the snapshot deliberately when renderer output changes.
