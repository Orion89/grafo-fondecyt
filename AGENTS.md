# AGENTS.md

## Stack

- Python 3.9 (pinned in `runtime.txt` and `Pipfile`)
- Plotly Dash 2.16.1 with `use_pages=True` (multi-page)
- Dash Bootstrap Components (`dbc.themes.FLATLY`)
- NetworkX + Pyvis + DashVis (vis.js wrapper) for graph rendering
- Deployed on Railway via Gunicorn

## Running locally

```bash
pip install -r requirements.txt   # pinned deps; use this, not Pipfile
python app.py                      # binds 0.0.0.0:8050
```

`debug=False` is hardcoded in `app.py` — change to `True` for hot-reload during development.

The app **must be launched from the repo root** — all data paths are relative (`./data/...`).

## Deployment

```
gunicorn main:server
```

**Procfile quirk:** `Procfile` references `main:server` but the server object (`server = app.server`) lives in `app.py`, not a `main.py`. No `main.py` exists in the repo. This is a known mismatch — do not create `main.py` without verifying the Railway config.

## Architecture

```
app.py              # Dash app init, navbar, layout shell, server export
data_process.py     # Graph-building utilities (NetworkX → Pyvis → JSON)
pages/
  page1.py          # KG of Fondecyt projects — registered at path '/'
  page2.py          # Researcher co-occurrence network — path '/page2'
network_options/
  options.py        # vis.js physics/interaction config dicts (imported by page2)
data/               # Required data files (loaded at module import — see below)
assets/             # Dash auto-serves this directory (favicon, etc.)
static/             # Logo images served at ./static/
```

## Data files — loaded at startup

All three files are loaded at **module import time**; missing files crash on startup:

| File | Loaded by |
|---|---|
| `data/proyectos_fondecyt_2012-2019.csv` | `pages/page1.py` |
| `data/g_researches_nx_v5.pkl` | `pages/page2.py` (pickle) |
| `data/centralities_measures.csv` | `pages/page2.py` |

`app.py` also loads the CSV but never uses it — that `df` is dead code.

Only `g_researches_nx_v5.pkl` is active; `v2`–`v4` and the un-versioned pickle are unused.

## Key function signatures

`data_process.filter_kgraph_nx_to_pyvis(df, year, university, k_layout)` — both `year` and `university` are required; omitting either raises `TypeError`.

## No tests, no linter, no CI

There is no test suite, no lint/format config, and no CI pipeline. Manual verification means running `python app.py` and checking the browser.

## Known dead / legacy code

- `kg_fondecyt_uai.json` — present in `data/` but commented out everywhere
- Several commented-out blocks in `app.py` and `page2.py` (old JSON network loading, node-select handler)
- `app.py` CSV load is unused

## Conventions

- `Pipfile`/`Pipfile.lock` are gitignored — only `requirements.txt` is tracked
- `todo.md` is gitignored
- Bootstrap Icons (`dbc.icons.BOOTSTRAP`) used for social icons in navbar/footer
- Primary accent color: `#3394D5`; graph background: `#222222`
