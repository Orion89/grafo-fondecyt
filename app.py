from ast import literal_eval
import json

import plotly.graph_objects as go
import plotly.express as px
import dash
from dash import Dash, dcc, html, Input, Output
import dash_bootstrap_components as dbc
from dashvis import DashNetwork, stylesheets

import networkx as nx
import pandas as pd

# from data_process import filter_kgraph_nx_to_pyvis

df = pd.read_csv('./data/proyectos_fondecyt_2012-2019.csv')

# with open('./data/kg_fondecyt_uai.json', 'r') as in_file:
#     network_data = json.load(in_file)
    

# network = DashNetwork(
#     id='g_fondecyt',
#     style={
#         'height': network_data['height'],
#         'width': network_data['width']
#     },
#     data={
#             'nodes': literal_eval(network_data['nodes']),
#             'edges': literal_eval(network_data['edges'])
#     }
# )

app = Dash(
    __name__,
    use_pages=True,
    title='Conexiones en los proyectos Fondecyt',
    external_stylesheets=[dbc.themes.FLATLY, stylesheets.VIS_NETWORK_STYLESHEET, dbc.icons.BOOTSTRAP],
    meta_tags=[
        {'name': 'viewport',
        'content': 'width=device-width, initial-scale=1.0'}
    ]
)

server = app.server

navbar = dbc.Nav(
    [
        dbc.NavItem(
            dbc.NavLink(page['name'], href=page['path'])
        ) for page in dash.page_registry.values()
    ],
    pills=True,
    # class_name='bg-light'
)

app.layout = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(
                    [
                        navbar
                    ],
                    width={'size': 7}
                ),
                dbc.Col(
                    [
                        html.P([
                            html.A(
                                children=[html.I(className="bi bi-github")],
                                disable_n_clicks=True,
                                href='https://github.com/Orion89',
                                title="GitHub profile"
                                    ),
                                "   ",
                                html.A(
                                    children=[html.I(className="bi bi-linkedin")],
                                    disable_n_clicks=True,
                                    href='https://www.linkedin.com/in/leonardo-molina-v-68a601183/',
                                    title="LinkedIn profile"
                                    ),
                                ]
                            ),
                    ],
                    align="center",
                    width={'size': 5},
                    class_name='mt-2 text-end fs-4'
                )
            ],
            class_name='bg-light'
        ),
        # dbc.Row( # HEADER
        #     [
        #         dbc.Col(
        #         [
        #             html.H1(
        #                 "Conexiones en los proyectos Fondecyt",
        #                 className="fw-bolder text-center"
        #             )
        #         ],
        #         width=12
        #         )
        #     ],
        #     class_name='m-2'
        # ),
        dbc.Row(
            [
                dbc.Col(
                    [
                     dash.page_container   
                    ],
                    width={'size': 12}
                )
            ]
        ),
        dbc.Row( # FOOTER
            [
                dbc.Col(
                    [
                        # html.Div(id='user-info', className='invisible m-0'),
                        dbc.Card(
                            [
                                dbc.CardFooter(
                                    [
                                        html.P([
                                            html.A(
                                                children=[html.I(className="bi bi-github")],
                                                disable_n_clicks=True,
                                                href='https://github.com/Orion89',
                                                title="GitHub profile"
                                            ),
                                            "  ",
                                            html.A(
                                                children=[html.I(className="bi bi-linkedin")],
                                                disable_n_clicks=True,
                                                href='https://www.linkedin.com/in/leonardo-molina-v-68a601183/',
                                                title="LinkedIn profile"
                                            ),
                                            " 2023 Leonardo Molina V."
                                            ],
                                            className='fs-5'
                                        ),
                                        html.P('Proyecto académico. El autor no se hace responsable del mal uso del contenido.')
                                    ]
                                    
                                )
                            ],
                        )
                    ],
                    class_name='mt-4',
                    width={'size': 12}
                )
            ],
            align='center',
            class_name='text-end'
        ),
    ],
    fluid=True
)


if __name__ == "__main__":
    app.run_server(debug=False, port="9000")