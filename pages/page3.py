"""
Página 3 — Tendencias del sistema Fondecyt (2012–2019)

Tres análisis exploratorios con storytelling:
  1. Hegemonía institucional: ¿se democratizó el financiamiento?
  2. Ascenso y caída de áreas: bump chart de rankings anuales
  3. Calidad de los proyectos: distribución de notas por área
"""

from __future__ import annotations

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import dash
from dash import dcc, html, callback, Input, Output, no_update
import dash_bootstrap_components as dbc


# ---------------------------------------------------------------------------
# Registro de página
# ---------------------------------------------------------------------------
dash.register_page(
    __name__,
    path="/tendencias",
    name="Tendencias del sistema",
    title="Tendencias Fondecyt 2012–2019",
    description="Análisis exploratorio de hegemonía institucional, evolución de áreas y calidad de proyectos",
)

# ---------------------------------------------------------------------------
# Constantes de estilo
# ---------------------------------------------------------------------------
ACCENT = "#3394D5"
BG_PLOT = "white"
GRID_COLOR = "#e8ecef"
TEXT_SECONDARY = "#6c757d"
FONT_FAMILY = "Open Sans, Arial, sans-serif"

AREA_LABELS: dict[str, str] = {
    "matematicas": "Matemáticas",
    "antrop. y arque": "Antropología y Arqueología",
    "astron.,cosmol.y par": "Astronomía y Cosmología",
    "filosofia": "Filosofía",
    "fisica teorica y exp": "Física",
    "biologia 1": "Biología 1",
    "cs. de la tierra": "Cs. de la Tierra",
    "linguistica,literatu": "Lingüística y Literatura",
    "historia": "Historia",
    "ingenieria 3": "Ingeniería 3",
    "ingenieria 2": "Ingeniería 2",
    "ingenieria 1": "Ingeniería 1",
    "quimica 1": "Química 1",
    "quimica 2": "Química 2",
    "cs. juridicas y pol.": "Cs. Jurídicas y Políticas",
    "sociologia cs i": "Sociología",
    "biologia 3": "Biología 3",
    "cs. econom/admi": "Cs. Económicas y Admin.",
    "biologia 2": "Biología 2",
    "agronomia": "Agronomía",
    "medicina g2-g3": "Medicina G2-G3",
    "educacion": "Educación",
    "geografia y urbanism": "Geografía y Urbanismo",
    "artes y arquitectura": "Artes y Arquitectura",
    "salud prod anim": "Salud y Prod. Animal",
    "sicologia": "Psicología",
    "medicina g1": "Medicina G1",
    "quimica": "Química",
}

# Instituciones con nombre abreviado para el gráfico
INST_SHORT: dict[str, str] = {
    "Univ. De Chile": "U. de Chile",
    "Pont. Univ. Catolica De Chile": "PUC",
    "Univ. De Santiago De Chile": "USACH",
    "Univ. Andres Bello": "UNAB",
    "Univ. Diego Portales": "UDP",
    "Univ. Adolfo Ibanez": "UAI",
    "Univ. De Los Andes": "U. Andes",
    "Univ. Alberto Hurtado": "UAH",
    "Univ. De Concepcion": "U. Concepción",
    "Univ. Tecnica Federico Santa Maria": "UTFSM",
}

YEARS = list(range(2012, 2020))

# ---------------------------------------------------------------------------
# Carga y preparación de datos (una sola vez al importar el módulo)
# ---------------------------------------------------------------------------
df_raw = pd.read_csv("./data/proyectos_fondecyt_2012-2019.csv")

# Un registro por proyecto (evitar duplicados por co-investigadores)
df_proj = df_raw.drop_duplicates("folioproy").copy()

# Normalizar nota_proyecto: 2012 usa escala 0–100, el resto usa 1–7
mask_2012 = df_proj["año_concurso"] == 2012
df_proj["nota_norm"] = df_proj["nota_proyecto"].copy()
df_proj.loc[mask_2012, "nota_norm"] = 1 + (df_proj.loc[mask_2012, "nota_proyecto"] / 100) * 6

# Etiquetas legibles para áreas
df_proj["area_label"] = df_proj["area_estudio"].map(AREA_LABELS).fillna(df_proj["area_estudio"])

# ---------------------------------------------------------------------------
# Datos para gráfico 1: Hegemonía institucional
# ---------------------------------------------------------------------------
TOP_N_INST = 8

_top_inst_global = (
    df_proj.groupby("institucion_patrocinante")["folioproy"]
    .count()
    .nlargest(TOP_N_INST)
    .index.tolist()
)

_inst_year = (
    df_proj.groupby(["año_concurso", "institucion_patrocinante"])["folioproy"]
    .count()
    .reset_index(name="n_proyectos")
)

# Agrupar instituciones fuera del top como "Otras"
_inst_year["inst_group"] = _inst_year["institucion_patrocinante"].apply(
    lambda x: x if x in _top_inst_global else "Otras universidades"
)
df_hegemony = (
    _inst_year.groupby(["año_concurso", "inst_group"])["n_proyectos"]
    .sum()
    .reset_index()
)
df_hegemony["inst_short"] = df_hegemony["inst_group"].map(INST_SHORT).fillna(
    df_hegemony["inst_group"]
)

# Orden de apilado: Otras al fondo, luego de menor a mayor
_order = ["Otras universidades"] + list(reversed(_top_inst_global))
_order_short = [INST_SHORT.get(i, i) for i in _order]

# Porcentaje por año
_total_year = df_hegemony.groupby("año_concurso")["n_proyectos"].transform("sum")
df_hegemony["pct"] = (df_hegemony["n_proyectos"] / _total_year * 100).round(1)

# ---------------------------------------------------------------------------
# Datos para gráfico 2: Bump chart de áreas
# ---------------------------------------------------------------------------
# Áreas con narrativa clara: las que más cambiaron + las más grandes
BUMP_AREAS_RAW = [
    "cs. juridicas y pol.",
    "astron.,cosmol.y par",
    "biologia 2",
    "biologia 3",
    "ingenieria 2",
    "matematicas",
    "medicina g1",
    "medicina g2-g3",
    "sociologia cs i",
    "educacion",
    "quimica 1",
    "historia",
]

_area_year_count = (
    df_proj.groupby(["año_concurso", "area_estudio"])["folioproy"]
    .count()
    .reset_index(name="n_proyectos")
)
_area_year_count["rank"] = (
    _area_year_count.groupby("año_concurso")["n_proyectos"]
    .rank(ascending=False, method="min")
    .astype(int)
)
df_bump = _area_year_count[_area_year_count["area_estudio"].isin(BUMP_AREAS_RAW)].copy()
df_bump["area_label"] = df_bump["area_estudio"].map(AREA_LABELS)

# ---------------------------------------------------------------------------
# Datos para gráfico 3: Distribución de notas por área
# ---------------------------------------------------------------------------
# Excluir "quimica" (solo 8 proyectos, escala diferente)
df_notas = df_proj[df_proj["area_estudio"] != "quimica"].copy()

# Ordenar áreas por mediana de nota normalizada
_area_median_order = (
    df_notas.groupby("area_label")["nota_norm"]
    .median()
    .sort_values(ascending=True)
    .index.tolist()
)

# ---------------------------------------------------------------------------
# Paleta de colores para instituciones y áreas del bump chart
# ---------------------------------------------------------------------------
_inst_palette = px.colors.qualitative.Bold
_inst_colors: dict[str, str] = {}
for i, inst in enumerate(_top_inst_global):
    short = INST_SHORT.get(inst, inst)
    _inst_colors[short] = _inst_palette[i % len(_inst_palette)]
_inst_colors["Otras universidades"] = "#ced4da"

# Paleta y colores del bump chart (necesarios en el callback)
_bump_palette = px.colors.qualitative.Alphabet
_bump_areas_labels = df_bump["area_label"].unique().tolist()
_bump_area_color: dict[str, str] = {
    a: _bump_palette[i % len(_bump_palette)]
    for i, a in enumerate(_bump_areas_labels)
}
_BUMP_HIGHLIGHTED = {
    "Cs. Jurídicas y Políticas",
    "Astronomía y Cosmología",
    "Biología 2",
    "Ingeniería 2",
}


# ---------------------------------------------------------------------------
# Helpers de layout de figura
# ---------------------------------------------------------------------------
def _base_layout(**kwargs) -> dict:
    base = dict(
        font=dict(family=FONT_FAMILY, color="#2c3e50"),
        paper_bgcolor=BG_PLOT,
        plot_bgcolor=BG_PLOT,
        margin=dict(l=20, r=20, t=50, b=20),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=11),
        ),
        hoverlabel=dict(
            bgcolor="white",
            font_size=13,
            font_family=FONT_FAMILY,
        ),
    )
    base.update(kwargs)
    return base


# ---------------------------------------------------------------------------
# Construcción de figuras
# ---------------------------------------------------------------------------

def build_hegemony_fig() -> go.Figure:
    """Área apilada normalizada (100%) de proyectos por institución y año."""
    fig = go.Figure()

    for inst_short in _order_short:
        subset = df_hegemony[df_hegemony["inst_short"] == inst_short].sort_values("año_concurso")
        if subset.empty:
            continue
        color = _inst_colors.get(inst_short, "#ced4da")
        fig.add_trace(
            go.Scatter(
                x=subset["año_concurso"],
                y=subset["pct"],
                name=inst_short,
                mode="lines",
                stackgroup="one",
                groupnorm="percent",
                line=dict(width=0.5, color=color),
                fillcolor=color,
                hovertemplate=(
                    "<b>%{fullData.name}</b><br>"
                    "Año: %{x}<br>"
                    "Participación: %{y:.1f}%<extra></extra>"
                ),
            )
        )

    fig.update_layout(
        **_base_layout(
            yaxis=dict(
                title="Participación (%)",
                ticksuffix="%",
                showgrid=True,
                gridcolor=GRID_COLOR,
                range=[0, 100],
            ),
            xaxis=dict(
                title="Año de concurso",
                tickmode="array",
                tickvals=YEARS,
                showgrid=False,
            ),
            hovermode="x unified",
            legend=dict(
                orientation="h",
                yanchor="top",
                y=-0.15,
                xanchor="center",
                x=0.5,
                font=dict(size=11),
                traceorder="reversed",
            ),
        )
    )
    return fig


def build_bump_fig(selected_area: str | None = None) -> go.Figure:
    """Bump chart: ranking de áreas por año.

    Args:
        selected_area: etiqueta del área a resaltar. Si es None se aplica el
                       resaltado por defecto (áreas con mayor movimiento).
    """
    fig = go.Figure()

    for area_label in _bump_areas_labels:
        subset = df_bump[df_bump["area_label"] == area_label].sort_values("año_concurso")
        color = _bump_area_color[area_label]

        if selected_area is None:
            # Comportamiento por defecto: resaltar las de mayor movimiento
            is_active = area_label in _BUMP_HIGHLIGHTED
        else:
            is_active = area_label == selected_area

        opacity = 1.0 if is_active else 0.15
        width = 3 if is_active else 1.0
        marker_size = 9 if is_active else 5

        fig.add_trace(
            go.Scatter(
                x=subset["año_concurso"],
                y=subset["rank"],
                name=area_label,
                mode="lines+markers",
                line=dict(color=color, width=width),
                marker=dict(size=marker_size, color=color),
                opacity=opacity,
                hovertemplate=(
                    f"<b>{area_label}</b><br>"
                    "Año: %{x}<br>"
                    "Ranking: #%{y}<br>"
                    "Proyectos: %{customdata}<extra></extra>"
                ),
                customdata=subset["n_proyectos"].values,
            )
        )

        # Etiqueta al final (año 2019) solo para el área activa
        if is_active:
            last = subset[subset["año_concurso"] == 2019]
            if not last.empty:
                fig.add_annotation(
                    x=2019,
                    y=last["rank"].values[0],
                    text=f"  {area_label}",
                    showarrow=False,
                    xanchor="left",
                    font=dict(size=11, color=color, family=FONT_FAMILY),
                )

    fig.update_layout(
        **_base_layout(
            yaxis=dict(
                title="Posición en el ranking",
                autorange="reversed",
                tickmode="linear",
                tick0=1,
                dtick=1,
                showgrid=True,
                gridcolor=GRID_COLOR,
                range=[0.5, 14],
            ),
            xaxis=dict(
                title="Año de concurso",
                tickmode="array",
                tickvals=YEARS,
                showgrid=False,
                range=[2011.5, 2020.5],
            ),
            showlegend=False,
            hovermode="closest",
            margin=dict(l=20, r=200, t=50, b=20),
        )
    )
    return fig


def _blue_shade(val: float, med_min: float, med_max: float) -> str:
    """Devuelve un color RGB en degradado azul según la posición de val en [med_min, med_max]."""
    t = (val - med_min) / (med_max - med_min) if med_max > med_min else 0.5
    r = int(30 + (1 - t) * 180)
    g = int(100 + (1 - t) * 100)
    b = int(180 + t * 75)
    return f"rgb({r},{g},{b})"


def build_notas_fig(year: int | None = None) -> go.Figure:
    """Box plot horizontal de nota normalizada por área, ordenado por mediana global.

    Args:
        year: si se especifica, filtra los datos a ese año de concurso.
    """
    data = df_notas if year is None else df_notas[df_notas["año_concurso"] == year]

    # Mediana global (para color consistente entre años)
    medians_global = df_notas.groupby("area_label")["nota_norm"].median()
    med_min = medians_global.min()
    med_max = medians_global.max()

    fig = go.Figure()

    for area in _area_median_order:
        vals = data[data["area_label"] == area]["nota_norm"].dropna()
        if vals.empty:
            continue
        n = len(vals)
        color = _blue_shade(medians_global.get(area, 4.5), med_min, med_max)

        fig.add_trace(
            go.Box(
                x=vals,
                name=area,
                orientation="h",
                marker_color=color,
                line_color=color,
                fillcolor=color,
                opacity=0.8,
                boxmean=True,
                hovertemplate=(
                    f"<b>{area}</b><br>"
                    "Mediana: %{median:.3f}<br>"
                    "Q1–Q3: %{q1:.3f} – %{q3:.3f}<br>"
                    f"n = {n} proyectos<extra></extra>"
                ),
            )
        )

    title = f"Año {year}" if year is not None else "Todos los años (2012–2019)"
    fig.update_layout(
        **_base_layout(
            title=dict(text=title, font=dict(size=13, color=TEXT_SECONDARY), x=0.5),
            xaxis=dict(
                title="Nota del proyecto (escala 1–7)",
                showgrid=True,
                gridcolor=GRID_COLOR,
                range=[3.8, 5.2],
            ),
            yaxis=dict(
                showgrid=False,
                tickfont=dict(size=11),
            ),
            showlegend=False,
            hovermode="y",
            margin=dict(l=200, r=20, t=50, b=40),
            height=700,
        )
    )
    return fig


def build_area_trend_fig(area_label: str) -> go.Figure:
    """Línea temporal de la mediana de nota normalizada para un área específica."""
    data = (
        df_notas[df_notas["area_label"] == area_label]
        .groupby("año_concurso")["nota_norm"]
        .agg(mediana="median", q1=lambda x: x.quantile(0.25), q3=lambda x: x.quantile(0.75), n="count")
        .reset_index()
    )

    color = _bump_area_color.get(area_label, ACCENT)

    fig = go.Figure()

    # Banda IQR
    fig.add_trace(
        go.Scatter(
            x=pd.concat([data["año_concurso"], data["año_concurso"].iloc[::-1]]),
            y=pd.concat([data["q3"], data["q1"].iloc[::-1]]),
            fill="toself",
            fillcolor=color,
            line=dict(color="rgba(0,0,0,0)"),
            opacity=0.15,
            hoverinfo="skip",
            showlegend=False,
            name="IQR",
        )
    )

    # Línea de mediana
    fig.add_trace(
        go.Scatter(
            x=data["año_concurso"],
            y=data["mediana"],
            mode="lines+markers",
            line=dict(color=color, width=2.5),
            marker=dict(size=8, color=color),
            name="Mediana",
            hovertemplate=(
                "Año: %{x}<br>"
                "Mediana: %{y:.3f}<br>"
                "n = %{customdata} proyectos<extra></extra>"
            ),
            customdata=data["n"].values,
        )
    )

    fig.update_layout(
        **_base_layout(
            title=dict(
                text=f"Evolución de la nota — {area_label}",
                font=dict(size=13),
                x=0.5,
            ),
            xaxis=dict(
                tickmode="array",
                tickvals=YEARS,
                showgrid=False,
            ),
            yaxis=dict(
                title="Nota (escala 1–7)",
                showgrid=True,
                gridcolor=GRID_COLOR,
                range=[3.8, 5.4],
            ),
            showlegend=False,
            hovermode="x unified",
            margin=dict(l=50, r=20, t=50, b=40),
            height=260,
        )
    )
    return fig


# ---------------------------------------------------------------------------
# Layout
# ---------------------------------------------------------------------------

def _section_header(
    title: str,
    subtitle: str,
    story: str,
    badge_text: str | None = None,
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
                    html.P(story, className="text-muted lh-base mb-0", style={"maxWidth": "820px"}),
                ],
                width=12,
            )
        ],
        className="mb-3 mt-2",
    )


layout = html.Div(
    [
        # ── Encabezado de página ──────────────────────────────────────────
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.H2(
                            "¿Cómo cambió la ciencia chilena entre 2012 y 2019?",
                            className="fw-bold mb-1",
                        ),
                        html.P(
                            "Ocho años de concursos Fondecyt revelan patrones que van más allá de los números: "
                            "quién concentra el poder, qué disciplinas ganan terreno y cómo se evalúa la calidad "
                            "de la investigación en Chile.",
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
        # SECCIÓN 1 — Hegemonía institucional
        # ══════════════════════════════════════════════════════════════════
        _section_header(
            title="El duopolio que no cede",
            subtitle="Participación de cada universidad en el total de proyectos adjudicados por año",
            story=(
                "La Universidad de Chile y la PUC concentraron más del 50% de todos los proyectos "
                "Fondecyt durante los ocho años analizados. En 2012 esa cifra llegó al 60%. "
                "Aunque la tendencia muestra una leve apertura hacia 2017–2018, el sistema sigue "
                "siendo profundamente asimétrico: el 90% de las universidades del país compite "
                "por el 40% restante del financiamiento."
            ),
            badge_text="01",
        ),
        dbc.Row(
            [
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody(
                            dcc.Graph(
                                id="hegemony-chart",
                                figure=build_hegemony_fig(),
                                config={"displayModeBar": False},
                                style={"height": "420px"},
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
        # SECCIÓN 2 — Bump chart de áreas
        # ══════════════════════════════════════════════════════════════════
        _section_header(
            title="Disciplinas que suben, disciplinas que caen",
            subtitle="Ranking anual de áreas de estudio según número de proyectos adjudicados",
            story=(
                "No todas las disciplinas corrieron la misma suerte. Las Ciencias Jurídicas y Políticas "
                "pasaron del puesto 7 en 2012 al liderazgo absoluto en 2019, mientras que Biología 2 "
                "cayó del top-5 al puesto 17 en el mismo período. Astronomía y Cosmología protagonizó "
                "el ascenso más espectacular: del puesto 19 al 6. "
                "Las líneas resaltadas marcan las trayectorias con mayor movimiento."
            ),
            badge_text="02",
        ),
        dbc.Row(
            [
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody(
                            dcc.Graph(
                                id="bump-chart",
                                figure=build_bump_fig(),
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
        # SECCIÓN 3 — Distribución de notas
        # ══════════════════════════════════════════════════════════════════
        _section_header(
            title="¿Todas las disciplinas son evaluadas igual?",
            subtitle=(
                "Distribución de la nota de evaluación por área de estudio "
                "(escala 1–7, nota normalizada; se excluye 'Química' por muestra insuficiente)"
            ),
            story=(
                "La nota de un proyecto Fondecyt no es solo un número: es el veredicto de pares "
                "que decide qué investigación merece financiamiento. Matemáticas lidera con la "
                "mediana más alta (4.76) y la menor dispersión, lo que sugiere consenso evaluativo. "
                "En el extremo opuesto, Medicina G1 tiene la mediana más baja (4.29) y una cola "
                "larga hacia abajo. La línea central de cada caja es la mediana; el rombo, el promedio. "
                "Cuando ambos se separan, hay proyectos muy bien o muy mal evaluados que distorsionan el promedio."
            ),
            badge_text="03",
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Row(
                            [
                                dbc.Col(
                                    dbc.Card(
                                        dbc.CardBody(
                                            [
                                                html.H2(
                                                    "4.76",
                                                    className="fw-bold mb-0",
                                                    style={"color": ACCENT},
                                                ),
                                                html.P(
                                                    "Mediana más alta",
                                                    className="text-secondary mb-0 small",
                                                ),
                                                html.P(
                                                    "Matemáticas",
                                                    className="fw-semibold mb-0",
                                                ),
                                            ]
                                        ),
                                        className="shadow-sm border-0 text-center h-100",
                                    ),
                                    width=4,
                                ),
                                dbc.Col(
                                    dbc.Card(
                                        dbc.CardBody(
                                            [
                                                html.H2(
                                                    "4.29",
                                                    className="fw-bold mb-0",
                                                    style={"color": "#e07b54"},
                                                ),
                                                html.P(
                                                    "Mediana más baja",
                                                    className="text-secondary mb-0 small",
                                                ),
                                                html.P(
                                                    "Medicina G1",
                                                    className="fw-semibold mb-0",
                                                ),
                                            ]
                                        ),
                                        className="shadow-sm border-0 text-center h-100",
                                    ),
                                    width=4,
                                ),
                                dbc.Col(
                                    dbc.Card(
                                        dbc.CardBody(
                                            [
                                                html.H2(
                                                    "0.47",
                                                    className="fw-bold mb-0",
                                                    style={"color": "#6c757d"},
                                                ),
                                                html.P(
                                                    "Diferencia mediana máx–mín",
                                                    className="text-secondary mb-0 small",
                                                ),
                                                html.P(
                                                    "Brecha entre disciplinas",
                                                    className="fw-semibold mb-0",
                                                ),
                                            ]
                                        ),
                                        className="shadow-sm border-0 text-center h-100",
                                    ),
                                    width=4,
                                ),
                            ],
                            className="mb-3 g-3",
                        ),
                        dbc.Card(
                            dbc.CardBody(
                                dcc.Graph(
                                    id="notas-chart",
                                    figure=build_notas_fig(),
                                    config={"displayModeBar": False},
                                )
                            ),
                            className="shadow-sm border-0",
                        ),
                    ],
                    width=12,
                )
            ],
            className="mb-5",
        ),

        # ── Nota metodológica ─────────────────────────────────────────────
        dbc.Row(
            [
                dbc.Col(
                    html.P(
                        [
                            html.I(className="bi bi-info-circle me-1"),
                            "Nota metodológica: los datos corresponden a proyectos Fondecyt Regular, "
                            "Iniciación y Postdoctorado adjudicados entre 2012 y 2019. "
                            "La nota de 2012 fue normalizada a escala 1–7 (originalmente en escala 0–100). "
                            "Cada proyecto se cuenta una sola vez, independientemente del número de investigadores.",
                        ],
                        className="text-muted small fst-italic",
                    ),
                    width=12,
                )
            ],
            className="mt-2 mb-4 pt-3 border-top",
        ),
    ],
    className="px-3",
)
