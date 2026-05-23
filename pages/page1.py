from ast import literal_eval

import plotly.graph_objects as go
import plotly.express as px
import dash
from dash import dcc, html, callback, Input, Output
import dash_bootstrap_components as dbc
from dashvis import DashNetwork

import networkx as nx
import pandas as pd

from data_process import filter_kgraph_nx_to_pyvis

dash.register_page(
    __name__,
    path="/",
    name="Grafo de proyectos Fondecyt",
    title="Grafo de proyectos",
    description="Grafo de conocimiento de proyectos Fondecyt: Visualiza investigadores, proyectos, áreas de estudio y universidades.",
)

df = pd.read_csv("./data/proyectos_fondecyt_2012-2019.csv")


def _section_header(
    title: str,
    subtitle: str,
    story: str,
    badge_text=None,
    title_id=None,
) -> dbc.Row:
    """Encabezado narrativo reutilizable para cada sección."""
    badge = (
        dbc.Badge(badge_text, color="primary", className="me-2 fs-6")
        if badge_text
        else None
    )

    h3_kwargs = {"className": "d-inline fw-bold mb-1"}
    if title_id:
        h3_kwargs["id"] = title_id

    return dbc.Row(
        [
            dbc.Col(
                [
                    html.Div(
                        [
                            badge,
                            html.H3(title, **h3_kwargs),
                        ],
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
        className="mb-3 mt-4",
    )


layout = html.Div(
    [
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.H1(
                            "Conectando Mentes, Financiando el Futuro",
                            className="fw-bold text-primary mb-3",
                        ),
                        html.H5(
                            "La ciencia no ocurre en el vacío; ocurre en el cruce entre la curiosidad de un investigador y el respaldo de una institución.",
                            className="text-secondary mb-4",
                        ),
                        html.P(
                            [
                                "Entre 2012 y 2019, Chile tejió una red de conocimiento sin precedentes a través de miles de adjudicaciones FONDECYT. "
                                "Este proyecto es la ",
                                html.B("huella digital del progreso científico nacional"),
                                ". Te invitamos a navegar por este ecosistema interactivo para mapear la colaboración, rastrear el talento e identificar las tendencias que lideran la agenda científica.",
                            ],
                            className="text-muted lh-base fs-5",
                        ),
                    ],
                    width=8,
                ),
                dbc.Col(
                    [
                        html.Img(
                            src="./static/Logo-Fondecyt-1.png",
                            style={"maxWidth": "300px", "width": "100%"},
                            className="float-end",
                        )
                    ],
                    width=4,
                    align="start",
                ),
            ],
            className="mb-5 mt-5",
        ),
        # ══════════════════════════════════════════════════════════════════
        # SECCIÓN 01 — Grafo de Conocimiento
        # ══════════════════════════════════════════════════════════════════
        _section_header(
            title="Ecosistema de Colaboración Científica",
            subtitle="Explorando el tejido de la ciencia nacional",
            story=(
                "Detrás de cada descubrimiento hay una red invisible de mentes y recursos. "
                "Este grafo de conocimiento permite desentrañar el tejido de la ciencia en Chile, "
                "conectando investigadores, proyectos, áreas del saber y universidades."
            ),
            badge_text="01",
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.Div(
                            [
                                html.I(className="bi bi-info-circle me-2"),
                                html.Small(
                                    "Interactúa con la red: Haz click en los nodos, arrástralos para reorganizar tu vista, "
                                    "usa el scroll del ratón para hacer zoom y deja el puntero sobre un nodo para revelar sus detalles."
                                ),
                            ],
                            className="text-secondary mb-3",
                        ),
                    ],
                    width=12,
                )
            ]
        ),
        dbc.Row(
            [
                # Columna Izquierda: Storytelling de los Datos (Ancho 2)
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody(
                            [
                                html.H5(
                                    [
                                        html.I(className="bi bi-database me-2 text-primary"),
                                        "La Huella Científica de Chile",
                                    ],
                                    className="fw-bold mb-3 text-primary",
                                    style={"fontSize": "1.1rem"},
                                ),
                                html.P(
                                    "Este visualizador se nutre de un registro histórico que documenta el latido de la ciencia nacional: "
                                    "miles de proyectos FONDECYT adjudicados entre 2012 y 2019. Cada registro captura no solo los "
                                    "nombres de los investigadores que lideran el conocimiento, sino también sus áreas de estudio "
                                    "(desde física y biología hasta historia y sociología), las notas de evaluación académica obtenidas, "
                                    "y los instrumentos de financiamiento público (Iniciación, Regular o Postdoctorado) que viabilizan sus ideas. "
                                    "Es la radiografía de cómo se distribuyen y florecen los recursos de investigación a lo largo del país.",
                                    className="text-muted lh-base mb-0",
                                    style={"fontSize": "0.85rem", "textAlign": "justify"},
                                ),
                            ],
                            className="p-3",
                        ),
                        className="shadow-sm border-0 border-start border-primary border-4 h-100",
                        style={"backgroundColor": "#f8f9fa"},
                    ),
                    width=2,
                    class_name="mb-1 d-flex align-items-stretch",
                ),
                # Columna Central: El Grafo (Ancho 8)
                dbc.Col(
                    [
                        dbc.Spinner(
                            html.Div(
                                id="network-1",
                                className="border-2 border-top border-primary",
                            ),
                            color="info",
                        )
                    ],
                    width=8,
                    class_name="mb-1",
                ),
                # Columna Derecha: Construcción del Grafo (Ancho 2)
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody(
                            [
                                html.H5(
                                    [
                                        html.I(className="bi bi-diagram-3 me-2 text-info"),
                                        "Anatomía de la Red",
                                    ],
                                    className="fw-bold mb-3 text-info",
                                    style={"fontSize": "1.1rem"},
                                ),
                                html.P(
                                    "Para dar sentido a miles de registros, la aplicación mapea dinámicamente cada dato a una estructura relacional. "
                                    "Las universidades, los proyectos, los años, las disciplinas académicas y los propios investigadores se transforman en nodos interconectados. "
                                    "Las líneas (o aristas) revelan relaciones clave, como qué científico participa en qué proyecto o qué institución lo patrocina. "
                                    "Finalmente, mediante un algoritmo de fuerzas físicas, los nodos se ordenan y repelen de forma automática en pantalla, "
                                    "revelando clústeres espontáneos que exponen la densidad de la colaboración y las sinergias institucionales.",
                                    className="text-muted lh-base mb-0",
                                    style={"fontSize": "0.85rem", "textAlign": "justify"},
                                ),
                            ],
                            className="p-3",
                        ),
                        className="shadow-sm border-0 border-start border-info border-4 h-100",
                        style={"backgroundColor": "#f8f9fa"},
                    ),
                    width=2,
                    class_name="mb-1 d-flex align-items-stretch",
                ),
            ],
            class_name="mb-3 mt-1 g-3",
        ),
        dbc.Row(
            [
                dbc.Col(
                    dbc.Container(
                        [
                            dcc.Dropdown(
                                options=df["institucion_patrocinante"]
                                .unique()
                                .tolist(),
                                value="Univ. Adolfo Ibanez",
                                multi=False,
                                clearable=False,
                                searchable=True,
                                id="dropdown-1",
                            )
                        ]
                    ),
                    width={"size": 5, "offset": 1},
                    class_name="mb-3",
                ),
                dbc.Col(
                    [
                        dcc.Slider(
                            min=int(df["año_concurso"].min()),
                            max=int(df["año_concurso"].max()),
                            step=None,
                            value=2019,
                            included=False,
                            marks={
                                int(year): str(year)
                                for year in df["año_concurso"].unique()
                            },
                            id="slider-1",
                        )
                    ],
                    width={"size": 5},
                    class_name="mb-3",
                ),
            ],
            justify="around",
            class_name="mb-3 border-2 border-bottom border-primary ",
        ),
        # ══════════════════════════════════════════════════════════════════
        # SECCIÓN 1 — Mapa de Prioridades
        # ══════════════════════════════════════════════════════════════════
        _section_header(
            title="Mapa de Prioridades de Investigación",
            subtitle="¿Qué frentes del conocimiento lideran la agenda institucional?",
            story=(
                "No todas las instituciones apuestan por los mismos frentes del conocimiento. "
                "Este mapa de rectángulos revela el ecosistema de prioridades de la universidad: "
                "el tamaño de cada bloque es proporcional al número de proyectos adjudicados en cada disciplina. "
                "Es, en esencia, la huella digital del impacto científico de la institución."
            ),
            badge_text="02",
            title_id="title-treemap-1",
        ),
        dbc.Row(
            [
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody(
                            dcc.Graph(
                                id="treemap-1",
                                config={"displayModeBar": False},
                                style={"height": "500px"},
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
        # SECCIÓN 2 — Proporción por tipo de proyecto
        # ══════════════════════════════════════════════════════════════════
        _section_header(
            title="Proporción por tipo de proyecto",
            subtitle="¿Cómo se distribuye la inversión entre investigadores nóveles y consolidados?",
            story=(
                "El equilibrio entre los distintos instrumentos de financiamiento habla de la madurez "
                "y renovación del cuerpo académico. Los proyectos Regulares consolidan líneas de investigación, "
                "mientras que Iniciación y Postdoctorado son el motor de renovación y atracción de nuevos talentos."
            ),
            badge_text="03",
        ),
        dbc.Row(
            [
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody(
                            dcc.Graph(
                                id="donut-1",
                                config={"displayModeBar": False},
                                style={"height": "500px"},
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


@callback(
    Output("network-1", "children"),
    Input("dropdown-1", "value"),
    Input("slider-1", "value"),
)
def create_network(u_name, year):
    G_data = filter_kgraph_nx_to_pyvis(
        df=df, year=year, university=u_name, k_layout=0.4
    )
    network = DashNetwork(
        id="g_fondecyt",
        style={"height": G_data["height"], "width": G_data["width"]},
        data={
            "nodes": literal_eval(G_data["nodes"]),
            "edges": literal_eval(G_data["edges"]),
        },
    )
    return network


@callback(
    Output("treemap-1", "figure"),
    Output("title-treemap-1", "children"),
    Input("dropdown-1", "value"),
)
def update_treemap_1(u_name):
    df_filtered = (
        df[df.institucion_patrocinante == u_name]["area_estudio"]
        .value_counts()
        .to_frame()
        .reset_index()
        .rename({"count": "frecuencia"}, axis=1)
        .copy()
    )

    fig = px.treemap(
        df_filtered,
        path=[px.Constant("Áreas"), "area_estudio"],
        values="frecuencia",
        color_discrete_sequence=px.colors.sequential.Blues_r,
    )
    fig.update_traces(root_color="lightgrey")
    fig.update_traces(
        textinfo="label+percent entry",
        insidetextfont=dict(
            # color='black',
            family="Opens Sans, Arial",
            size=16,
        ),
    )
    fig.update_layout(margin=dict(t=20, l=25, r=25, b=25))

    title = f"Mapa de Prioridades de Investigación de la {u_name}"

    return fig, title


@callback(Output("donut-1", "figure"), Input("dropdown-1", "value"))
def update_donut_1(u_name):
    df_filtered = (
        df[df.institucion_patrocinante == u_name]["instrumento"]
        .value_counts()
        .to_frame()
        .reset_index()
        .rename({"instrumento": "Tipo de instrumento", "count": "frecuencia"}, axis=1)
        .copy()
    )

    fig = px.pie(
        data_frame=df_filtered,
        names="Tipo de instrumento",
        values="frecuencia",
        color_discrete_sequence=px.colors.sequential.Blues_r,
        hole=0.5,
    )
    fig.update_traces(
        textposition="outside",
        textinfo="percent+label",
        texttemplate="%{label}<br>%{percent:.1%}",
        textfont={"size": 16},
    )
    fig.update_layout(showlegend=False)

    return fig
