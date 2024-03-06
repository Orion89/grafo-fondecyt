from ast import literal_eval
import json

from dash import Dash, dcc, html, Input, Output
import dash_bootstrap_components as dbc
from dashvis import DashNetwork, stylesheets

import networkx as nx
import pandas as pd

from data_process import filter_graph_nx_to_pyvis

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
    title='Conexiones en los proyectos Fondecyt',
    external_stylesheets=[dbc.themes.FLATLY, stylesheets.VIS_NETWORK_STYLESHEET],
    meta_tags=[
        {'name': 'viewport',
        'content': 'width=device-width, initial-scale=1.0'}
    ]
)

app.layout = dbc.Container(
    [
        dbc.Row(
            dbc.Col(
                [
                    html.H1(
                        "Conexiones en los proyectos Fondecyt",
                        className="fw-bolder text-center"
                    )
                ],
                width=12
            ),
            class_name='m-2'
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.H2("Grafo"),
                        dbc.Container(
                            # network,
                            id='network-1'
                        )
                    ],
                    width=12,
                    class_name='mb-1'
                )
            ]
        ),
        dbc.Row(
            [
                dbc.Col(
                    dbc.Container(
                    [
                        dcc.Dropdown(
                            options=df['institucion_patrocinante'].unique().tolist(),
                            value='Univ. Adolfo Ibanez',
                            multi=False,
                            clearable=False,
                            searchable=True,
                            id='dropdown-1'
                        )
                    ]
                ),
                    width={
                        'size': 4,
                        'offset': 1
                    }
                ),
                dbc.Col(
                    dcc.Slider(
                        min=int(df['año_concurso'].min()),
                        max=int(df['año_concurso'].max()),
                        step=None,
                        value=2019,
                        marks={int(year): str(year) for year in df['año_concurso'].unique()},
                        id='slider-1'
                    )
                )
            ]
        )
    ]
)

@app.callback(
    Output('network-1', 'children'),
    Input('dropdown-1', 'value'),
    Input('slider-1', 'value')
)
def create_network(u_name, year):
    G_data = filter_graph_nx_to_pyvis(df=df, year=year, university=u_name, k_layout=0.4)
    network = DashNetwork(
        id='g_fondecyt',
        style={
            'height': G_data['height'],
            'width': G_data['width']
        },
        data={
            'nodes': literal_eval(G_data['nodes']),
            'edges': literal_eval(G_data['edges'])
        }
    )
    return network


if __name__ == "__main__":
    app.run_server(debug=True, port="9000")