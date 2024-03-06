from ast import literal_eval
import json

from dash import Dash, dcc, html
import dash_bootstrap_components as dbc
from dashvis import DashNetwork, stylesheets

import networkx as nx
import pandas as pd

with open('./data/kg_fondecyt_uai.json', 'r') as in_file:
    network_data = json.load(in_file)
    

network = DashNetwork(
    id='g_fondecyt',
    style={
        'height': network_data['height'],
        'width': network_data['width']
    },
    data={
            'nodes': literal_eval(network_data['nodes']),
            'edges': literal_eval(network_data['edges'])
    }
)

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
                html.H2("Grafo"),
                network
                
            ]
        )
    ]
)

if __name__ == "__main__":
    app.run_server(debug=True, port="9000")