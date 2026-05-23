"""
Página 3 — Trayectorias e investigadores

Análisis de la movilidad institucional, colaboración interdisciplinaria y evolución de carrera de los investigadores Fondecyt.
"""

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import dash
from dash import dcc, html, callback, Input, Output
import dash_bootstrap_components as dbc
import numpy as np

dash.register_page(
    __name__,
    path="/trayectorias",
    name="Trayectorias e investigadores",
    title="Trayectorias e investigadores",
    description="Análisis de movilidad, colaboración entre áreas y evolución de postdoctorados.",
)

# Load data
df = pd.read_csv("./data/proyectos_fondecyt_2012-2019.csv")


def get_mobility_data(df):
    # Filter researchers with more than one institution
    researcher_inst = (
        df.sort_values(["nombre_completo", "año_concurso"])
        .groupby("nombre_completo")["institucion_patrocinante"]
        .unique()
    )
    mobile_researchers = researcher_inst[researcher_inst.apply(len) > 1]

    transitions = []
    for inst_list in mobile_researchers:
        for i in range(len(inst_list) - 1):
            transitions.append((inst_list[i], inst_list[i + 1]))

    transition_df = pd.DataFrame(transitions, columns=["source", "target"])
    counts = (
        transition_df.groupby(["source", "target"]).size().reset_index(name="value")
    )

    # Filter for top transitions to keep Sankey readable
    counts = counts.sort_values("value", ascending=False).head(40)

    all_nodes = list(pd.concat([counts["source"], counts["target"]]).unique())
    node_map = {node: i for i, node in enumerate(all_nodes)}

    sources = counts["source"].map(node_map).tolist()
    targets = counts["target"].map(node_map).tolist()
    values = counts["value"].tolist()

    return all_nodes, sources, targets, values


def get_area_collaboration_data(df):
    # Link areas if they share a researcher
    researcher_areas = df.groupby("nombre_completo")["area_estudio"].unique()

    links = []
    for areas in researcher_areas:
        if len(areas) > 1:
            areas = sorted(list(areas))
            for i in range(len(areas)):
                for j in range(i + 1, len(areas)):
                    links.append((areas[i], areas[j]))

    links_df = pd.DataFrame(links, columns=["area1", "area2"])
    matrix = links_df.groupby(["area1", "area2"]).size().reset_index(name="count")

    # Pivot to create a matrix
    areas = sorted(df["area_estudio"].unique())
    adj_matrix = pd.DataFrame(0, index=areas, columns=areas)

    for _, row in matrix.iterrows():
        adj_matrix.loc[row["area1"], row["area2"]] = row["count"]
        adj_matrix.loc[row["area2"], row["area1"]] = row["count"]

    return adj_matrix


def get_postdoc_transition_data(df):
    # Identify researchers who were POSTDOCTORADO
    postdocs = df[df["instrumento"] == "POSTDOCTORADO"]["nombre_completo"].unique()

    transitions = []
    for name in postdocs:
        researcher_data = df[df["nombre_completo"] == name].sort_values("año_concurso")
        postdoc_years = researcher_data[
            researcher_data["instrumento"] == "POSTDOCTORADO"
        ]["año_concurso"].tolist()
        pi_years = researcher_data[researcher_data["calidad"] == "INVEST. RESPONSABLE"][
            "año_concurso"
        ].tolist()

        # We look for the first PI role after the first Postdoc role
        if postdoc_years and pi_years:
            first_postdoc = min(postdoc_years)
            future_pi = [y for y in pi_years if y > first_postdoc]
            if future_pi:
                first_pi = min(future_pi)
                transitions.append((f"Postdoc ({first_postdoc})", f"PI ({first_pi})"))
            else:
                transitions.append((f"Postdoc ({first_postdoc})", "Solo Postdoc"))
        elif postdoc_years:
            first_postdoc = min(postdoc_years)
            transitions.append((f"Postdoc ({first_postdoc})", "Solo Postdoc"))

    transition_df = pd.DataFrame(transitions, columns=["source", "target"])
    counts = (
        transition_df.groupby(["source", "target"]).size().reset_index(name="value")
    )

    all_nodes = sorted(list(pd.concat([counts["source"], counts["target"]]).unique()))
    node_map = {node: i for i, node in enumerate(all_nodes)}

    sources = counts["source"].map(node_map).tolist()
    targets = counts["target"].map(node_map).tolist()
    values = counts["value"].tolist()

    return all_nodes, sources, targets, values


# ---------------------------------------------------------------------------
# Helpers de layout (estilo Página 2)
# ---------------------------------------------------------------------------


def _section_header(
    title: str,
    subtitle: str,
    story: str,
    badge_text=None,
) -> dbc.Row:
    """Encabezado narrativo reutilizable para cada sección."""
    badge = (
        dbc.Badge(badge_text, color="primary", className="me-2 fs-6")
        if badge_text
        else None
    )
    return dbc.Row(
        [
            dbc.Col(
                [
                    html.Div(
                        [badge, html.H3(title, className="d-inline fw-bold mb-1")],
                        className="mb-1",
                    ),
                    html.H6(subtitle, className="text-secondary mb-2"),
                    html.P(
                        story,
                        className="text-muted lh-base mb-0",
                        style={"maxWidth": "820px"},
                    ),
                ],
                width=12,
            )
        ],
        className="mb-3 mt-2",
    )


layout = html.Div(
    [
        # ── Encabezado de página (estilo Página 2) ────────────────────────
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.H2(
                            "Trayectorias e Investigadores",
                            className="fw-bold mb-1",
                        ),
                        html.P(
                            "Análisis de la movilidad institucional, colaboración interdisciplinaria y evolución de carrera de los investigadores Fondecyt.",
                            className="text-secondary fs-5 mb-0",
                            style={"maxWidth": "860px"},
                        ),
                    ],
                    width=12,
                )
            ],
            className="mt-4 mb-4 pb-3 border-bottom border-2 border-primary",
        ),
        # ══════════════════════════════════════════════════════════════════
        # SECCIÓN 1 — Movilidad Institucional
        # ══════════════════════════════════════════════════════════════════
        _section_header(
            title="Movilidad Institucional de Investigadores",
            subtitle="Flujo de investigadores entre instituciones",
            story=(
                "¿Quiénes son los 'conectores' del sistema? Este análisis sigue el flujo de investigadores "
                "que han trabajado en más de una institución a lo largo de su carrera. Puedes filtrar "
                "por área de estudio para observar patrones específicos de movilidad disciplinaria."
            ),
            badge_text="01",
        ),
        dbc.Row(
            [
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody(
                            [
                                dbc.Row(
                                    [
                                        dbc.Col(
                                            [
                                                html.Label(
                                                    "Filtrar por área de estudio:",
                                                    className="small text-muted mb-1",
                                                ),
                                                dcc.Dropdown(
                                                    id="mobility-area-filter",
                                                    options=[
                                                        {"label": area, "value": area}
                                                        for area in sorted(
                                                            df["area_estudio"].unique()
                                                        )
                                                    ],
                                                    placeholder="Todas las áreas",
                                                    multi=False,
                                                    clearable=True,
                                                    className="shadow-sm",
                                                ),
                                            ],
                                            width=12,
                                            md=6,
                                            lg=4,
                                            className="mb-3",
                                        )
                                    ]
                                ),
                                dbc.Spinner(
                                    dcc.Graph(
                                        id="sankey-mobility",
                                        config={"displayModeBar": False},
                                    ),
                                    color="info",
                                ),
                            ]
                        ),
                        className="shadow-sm border-0",
                    ),
                    width=12,
                )
            ],
            className="mb-5",
        ),
        # ══════════════════════════════════════════════════════════════════
        # SECCIÓN 2 — Colaboración entre Áreas
        # ══════════════════════════════════════════════════════════════════
        _section_header(
            title="Red de Colaboración entre Áreas",
            subtitle="Intensidad de investigadores compartidos entre disciplinas",
            story=(
                "¿Qué áreas de conocimiento colaboran entre sí? Este mapa revela qué disciplinas están "
                "más conectadas a través de sus investigadores. Los puentes entre clusters identifican "
                "actores estratégicos para la política científica nacional."
            ),
            badge_text="02",
        ),
        dbc.Row(
            [
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody(
                            dbc.Spinner(
                                dcc.Graph(
                                    id="heatmap-areas", config={"displayModeBar": False}
                                ),
                                color="info",
                            )
                        ),
                        className="shadow-sm border-0",
                    ),
                    width=12,
                )
            ],
            className="mb-5",
        ),
        # ══════════════════════════════════════════════════════════════════
        # SECCIÓN 3 — Postdoc -> PI
        # ══════════════════════════════════════════════════════════════════
        _section_header(
            title="El Efecto POSTDOCTORADO: ¿Trampolín o callejón sin salida?",
            subtitle="Trayectoria desde Postdoctorado hasta Investigador Responsable (PI)",
            story=(
                "El seguimiento de cohortes mide la efectividad de los proyectos de postdoctorado. "
                "¿Logran estos investigadores reaparecer como investigadores responsables en años posteriores? "
                "Este flujo temporal muestra la transición de carrera dentro del sistema Fondecyt."
            ),
            badge_text="03",
        ),
        dbc.Row(
            [
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody(
                            dbc.Spinner(
                                dcc.Graph(
                                    id="sankey-postdoc",
                                    config={"displayModeBar": False},
                                ),
                                color="info",
                            )
                        ),
                        className="shadow-sm border-0",
                    ),
                    width=12,
                )
            ],
            className="mb-5",
        ),
    ],
    className="px-3",
)


@callback(Output("sankey-mobility", "figure"), Input("mobility-area-filter", "value"))
def update_sankey_mobility(selected_area):
    filtered_df = df
    if selected_area:
        # Get researchers who worked in this area
        researchers_in_area = df[df["area_estudio"] == selected_area][
            "nombre_completo"
        ].unique()
        filtered_df = df[df["nombre_completo"].isin(researchers_in_area)]

    nodes, sources, targets, values = get_mobility_data(filtered_df)

    if not nodes:
        return go.Figure().update_layout(
            title="No hay datos de movilidad para este filtro"
        )

    fig = go.Figure(
        data=[
            go.Sankey(
                node=dict(
                    pad=15,
                    thickness=20,
                    line=dict(color="black", width=0.5),
                    label=[n[:35] + "..." if len(n) > 35 else n for n in nodes],
                    color="rgba(51, 148, 213, 0.8)",
                ),
                link=dict(
                    source=sources,
                    target=targets,
                    value=values,
                    color="rgba(145, 161, 162, 0.4)",
                ),
            )
        ]
    )

    fig.update_layout(
        font=dict(family="Open Sans, Arial, sans-serif", color="#2c3e50"),
        paper_bgcolor="white",
        plot_bgcolor="white",
        title_text=f"Flujo de Investigadores entre Instituciones {f' - {selected_area}' if selected_area else ''}",
        font_size=10,
        height=700,
    )
    return fig


@callback(Output("heatmap-areas", "figure"), Input("heatmap-areas", "id"))
def update_heatmap_areas(_):
    adj_matrix = get_area_collaboration_data(df)

    fig = px.imshow(
        adj_matrix,
        labels=dict(x="Área 1", y="Área 2", color="Investigadores compartidos"),
        x=adj_matrix.columns,
        y=adj_matrix.index,
        color_continuous_scale="Blues",
    )
    fig.update_layout(
        font=dict(family="Open Sans, Arial, sans-serif", color="#2c3e50"),
        paper_bgcolor="white",
        plot_bgcolor="white",
        title_text="Matriz de Adyacencia entre Áreas de Estudio",
        height=800,
    )
    return fig


@callback(Output("sankey-postdoc", "figure"), Input("sankey-postdoc", "id"))
def update_sankey_postdoc(_):
    nodes, sources, targets, values = get_postdoc_transition_data(df)

    fig = go.Figure(
        data=[
            go.Sankey(
                node=dict(
                    pad=15,
                    thickness=20,
                    line=dict(color="black", width=0.5),
                    label=nodes,
                    color="rgba(40, 167, 69, 0.8)",
                ),
                link=dict(
                    source=sources,
                    target=targets,
                    value=values,
                    color="rgba(40, 167, 69, 0.2)",
                ),
            )
        ]
    )

    fig.update_layout(
        font=dict(family="Open Sans, Arial, sans-serif", color="#2c3e50"),
        paper_bgcolor="white",
        plot_bgcolor="white",
        title_text="Trayectoria: Postdoc -> Investigador Responsable (PI)",
        font_size=10,
        height=600,
    )
    return fig
