from ast import literal_eval
import pickle

import networkx as nx
from pyvis.network import Network

import dash
from dash import html, dcc
from dashvis import DashNetwork
import dash_bootstrap_components as dbc

from data_process import nx_to_pyvis
from network_options import options

dash.register_page(
    __name__,
    name='Grafo investigadores',
    title='Grafo de investigadores',
    description='Grafo de co-ocurrencias de investigadores en proyectos Fondecyt'
)

with open('./data/g_researches_nx.pkl', 'rb') as in_file:
    nx_graph = pickle.load(in_file)
    
graph_data = nx_to_pyvis(nx_graph=nx_graph)

researchers_network = DashNetwork(
    id='network-2',
    style={
        'height': graph_data['height'],
        'width': graph_data['width']
    },
    data={
            'nodes': literal_eval(graph_data['nodes']),
            'edges': literal_eval(graph_data['edges'])
    },
    # enableHciEvents=False,
    # enablePhysicsEvents=True,
    # enableOtherEvents=False
)
    
layout = html.Div(
    [
        dbc.Row(
        [
            dbc.Col(
                [
                    html.H2(
                        'Explorando la Red Científica: Colaboraciones en Proyectos Fondecyt'
                    )
                ],
                width={'size': 7},
                align='start'
            ),
            dbc.Col(
                [
                    html.P(
                        '''
                        Haz zoom para ver los nodos con mayor detalle. Dejando el puntero sobre un nodo se desplegarán las universidades patrocinantes.
                        Dejando el puntero sobre una arista se verán los folios de los proyectos en los cuales participaron los nodos unidos. 
                        ''',
                        className='text-secondary fs-6 p-0 lh-sm text-end'
                    )
                ],
                width={'size': 5},
                align='end'
            )
        ],
        class_name='mt-4 mb-4'
    ),
    dbc.Row(
        [
            dbc.Col(
               [
                   dbc.Card(
                       [
                           dbc.CardBody(
                               [
                                   html.H4('Co-ocurrencias de investigadores', className='card-title'),
                                   html.H5('Redes de colaboración entre académicos', className='card-subtitle text-secondary'),
                                   html.Br(),
                                   html.P('Se estable una arista entre dos investigadores si han trabajado en el mismo proyecto. El grosor de la arista refleja el número de colaboraciones.', className='card-text text-info'),
                                   html.P('Se consideran todos los años del data set en conjunto. No se dibujan los investigadores sin colaboraciones.', className='card-text text-info')
                               ]
                           )
                       ]
                   )
               ],
               width={'size': 2} 
            ),
            dbc.Col(
                [
                    dbc.Spinner(
                            html.Div(
                                [researchers_network]
                            ),
                        color='info'
                    )
                ],
                width={'size': 10}
            )
        ]
    )
    ]
)
