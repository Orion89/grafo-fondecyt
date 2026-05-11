import os

import dash
import dash_bootstrap_components as dbc
from dash import Dash, html
from dashvis import stylesheets

app = Dash(
    __name__,
    use_pages=True,
    title="Conexiones en los proyectos Fondecyt",
    external_stylesheets=[
        dbc.themes.FLATLY,
        stylesheets.VIS_NETWORK_STYLESHEET,
        dbc.icons.BOOTSTRAP,
    ],
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1.0"}
    ],
)

server = app.server

navbar = dbc.Nav(
    [
        dbc.NavItem(dbc.NavLink(page["name"], href=page["path"], class_name="fw-bold"))
        for page in dash.page_registry.values()
    ],
    pills=True,
    # class_name='bg-light'
)

app.layout = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col([navbar], width={"size": 9}),
                dbc.Col(
                    [
                        html.P(
                            [
                                html.A(
                                    children=[html.I(className="bi bi-github")],
                                    disable_n_clicks=True,
                                    href="https://github.com/Orion89",
                                    title="GitHub profile",
                                ),
                                "   ",
                                html.A(
                                    children=[html.I(className="bi bi-linkedin")],
                                    disable_n_clicks=True,
                                    href="https://www.linkedin.com/in/leonardo-molina-v-68a601183/",
                                    title="LinkedIn profile",
                                ),
                            ]
                        ),
                    ],
                    align="center",
                    width={"size": 3},
                    class_name="mt-2 text-end fs-4",
                ),
            ],
            class_name="bg-light",
        ),
        dbc.Row([dbc.Col([dash.page_container], width={"size": 12})]),
        dbc.Row(  # FOOTER
            [
                dbc.Col(
                    [
                        dbc.Card(
                            [
                                dbc.CardFooter(
                                    [
                                        html.P(
                                            [
                                                html.A(
                                                    children=[
                                                        html.I(className="bi bi-github")
                                                    ],
                                                    disable_n_clicks=True,
                                                    href="https://github.com/Orion89",
                                                    title="GitHub profile",
                                                ),
                                                "  ",
                                                html.A(
                                                    children=[
                                                        html.I(
                                                            className="bi bi-linkedin"
                                                        )
                                                    ],
                                                    disable_n_clicks=True,
                                                    href="https://www.linkedin.com/in/leonardo-molina-v-68a601183/",
                                                    title="LinkedIn profile",
                                                ),
                                                " 2023-2026 Leonardo Molina V.",
                                            ],
                                            className="fs-5",
                                        ),
                                        html.P(
                                            "Proyecto académico. El autor no se hace responsable del mal uso del contenido."
                                        ),
                                    ]
                                )
                            ],
                        )
                    ],
                    class_name="mt-4",
                    width={"size": 12},
                )
            ],
            align="center",
            class_name="text-end",
        ),
    ],
    fluid=True,
)


if __name__ == "__main__":
    app.run(
        debug=False,
        host=os.getenv("HOST", default="0.0.0.0"),
        port=os.getenv("PORT", default="8050"),
    )
