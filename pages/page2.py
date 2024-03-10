from ast import literal_eval
import pickle

import networkx as nx
from pyvis.network import Network

import dash
from dash import html, dcc, callback, Input, Output, no_update
from dashvis import DashNetwork
import dash_bootstrap_components as dbc

from data_process import nx_to_pyvis_process
from network_options import options

dash.register_page(
    __name__,
    name='Grafo investigadores',
    title='Grafo de investigadores',
    description='Grafo de co-ocurrencias de investigadores en proyectos Fondecyt'
)

with open('./data/g_researches_nx_v4.pkl', 'rb') as in_file:
    nx_graph = pickle.load(in_file)
    
graph_data = nx_to_pyvis_process(nx_graph=nx_graph)

researchers_network = DashNetwork(
    id='network-2',
    style={
        'height': graph_data['height'],
        'width': graph_data['width']
    },
    options=options.default_options_,
    data={
            'nodes': literal_eval(graph_data['nodes']),
            'edges': literal_eval(graph_data['edges'])
    },
    enableHciEvents=True,
    enablePhysicsEvents=False,
    enableOtherEvents=False
)


modal = dbc.Modal(
    [
        dbc.ModalHeader(html.P("Cargando visualización...", className='fw-bold mb-0')),
        dbc.ModalBody(
            [
                html.P("El proceso de carga del grafo puede tardar unos minutos."),
                html.P('Puedes cerrar este cuadro.')
            ]
            ),
        dbc.ModalFooter(
            dbc.Button("Cerrar", id="modal-close", className="ml-auto", n_clicks=0)
        ),
    ],
    id="modal-1",
    is_open=True,
)
    
layout = html.Div(
    [
        modal,
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
    ),
    dbc.Row(
        [
            dbc.Col(
                [
                    html.Div(
                        id='select-node-event-1'
                    )
                ],
                width={'size': 6}
            )
        ],
        class_name='mt-2'
    )
    ]
)


@callback(
    Output('select-node-event-1', 'children'),
    Input('network-2', 'selectNode')
)
def node_select_event(selected_node):
    if selected_node:
        import pprint
    
        return '''
        Select node event produced:
        {}
        '''.format(pprint.pformat(selected_node, indent=4, width=200, compact=False, sort_dicts=True))
    else:
        return 'No se ha seleccionado un nodo'
    

@callback(
    Output("modal-1", "is_open"),
    [Input("modal-close", "n_clicks")],
)
def close_modal(n_clicks):
    if n_clicks > 0:
        return False
    return True