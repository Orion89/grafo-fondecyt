# Grafo FONDECYT - Project Documentation

This project is a multi-page Dash application designed to visualize and analyze FONDECYT (Chilean National Fund for Scientific and Technological Development) research projects and investigator collaboration networks.

## Project Overview

- **Purpose:** Provide an interactive interface to explore scientific research data, including knowledge graphs of projects and co-occurrence networks of researchers.
- **Main Technologies:**
    - **Frontend:** [Dash](https://dash.plotly.com/), [Dash Bootstrap Components](https://dash-bootstrap-components.opensource.faculty.ai/), [Dashvis](https://github.com/Orion89/dashvis).
    - **Data Processing:** [Pandas](https://pandas.pydata.org/), [NumPy](https://numpy.org/).
    - **Graph Analysis:** [NetworkX](https://networkx.org/), [Pyvis](https://pyvis.readthedocs.io/).
    - **Visualizations:** [Plotly](https://plotly.com/python/).
- **Architecture:**
    - Multi-page Dash application using `use_pages=True`.
    - Centralized data processing in `data_process.py`.
    - Page-specific layouts and callbacks in the `pages/` directory.

## Project Structure

- `app.py`: Main entry point. Defines the application instance, layout, and global navbar/footer.
- `data_process.py`: Contains utility functions for filtering data and converting NetworkX graphs to formats compatible with Pyvis/Dashvis.
- `pages/`: Contains the logic and layout for each page:
    - `page1.py`: Knowledge Graph of projects, filtered by university and year. Includes treemap and donut charts.
    - `page2.py`: Researcher co-occurrence network.
    - `page3.py`: (Likely additional network analysis or metrics).
- `data/`: Datasets used by the application (CSV, PKL, JSON).
- `network_options/`: Custom styling and configuration for network visualizations.
- `static/`, `assets/`, `img/`: Images, icons, and static assets.
- `requirements.txt`: Python dependencies.
- `Procfile`, `runtime.txt`: Deployment configurations (e.g., for Railway.app or Heroku).

## Building and Running

### Prerequisites
- Python (check `runtime.txt` for specific version, likely 3.10+).
- Dependencies listed in `requirements.txt`.

### Installation
```bash
pip install -r requirements.txt
```

### Running the Application
```bash
python app.py
```
By default, the app runs on `http://0.0.0.0:8050`.

## Development Conventions

- **Page Registration:** New pages should be added to the `pages/` directory and use `dash.register_page`.
- **Styling:** Uses Dash Bootstrap Components (`dbc.themes.FLATLY`) for layout and responsiveness.
- **Data Handling:** Data is typically loaded from `data/` using Pandas.
- **Graph Visualization:** The project heavily relies on `Dashvis` and `NetworkX` for interactive network diagrams.

## Key Files to Reference

- `app.py`: Application configuration and shared layout.
- `data_process.py`: Core graph transformation logic.
- `pages/page1.py`: Example of a page with complex callbacks and multiple visualizations.
- `README.md`: High-level description and visual examples of the graphs.

## General guidelines

### 1. Think Before Coding

**Don't assume. Don't hide confusion. Surface tradeoffs.**

Before implementing:
- State your assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them - don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.

### 2. Simplicity First

**Minimum code that solves the problem. Nothing speculative.**

- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- No error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.

Ask yourself: "Would a senior engineer say this is overcomplicated?" If yes, simplify.

### 3. Surgical Changes

**Touch only what you must. Clean up only your own mess.**

When editing existing code:
- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead code, mention it - don't delete it.

When your changes create orphans:
- Remove imports/variables/functions that YOUR changes made unused.
- Don't remove pre-existing dead code unless asked.

The test: Every changed line should trace directly to the user's request.
