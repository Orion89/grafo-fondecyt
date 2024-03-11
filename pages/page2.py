from ast import literal_eval
import pickle

import networkx as nx
import pandas as pd
from pyvis.network import Network

import dash
from dash import html, dcc, callback, Input, Output, no_update
from dashvis import DashNetwork
import dash_bootstrap_components as dbc
import plotly.graph_objects as go

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
    
graph_data, G_pyvis = nx_to_pyvis_process(nx_graph=nx_graph)
df_centralities_measures = pd.read_csv('./data/centralities_measures.csv')
df_centralities_measures.set_index('nombre_completo', inplace=True)

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
                    dcc.Graph(
                        id='nodes-comparison-1'
                    ),
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

@callback(
    Output('nodes-comparison-1', 'figure'),
    Output('nodes-comparison-1', 'className'),
    Input('network-2', 'selectNode')
)
def node_comparison(selected_node_dict):
    if not selected_node_dict:
        return no_update, 'invisible'
    node_selected_id = selected_node_dict['nodes'][0]
    node_label = G_pyvis.node_map[node_selected_id]['label']
    node_statistics = df_centralities_measures.loc[node_label]
    
    fig = go.Figure()
    points_graph = go.Scatter(
        x=node_statistics.values[:-2],
        y=node_statistics.index[:-2],
        name='Medidas de centralidad',
        marker=dict(
            color='rgba(156, 165, 196, 0.90)',
            line_color='rgba(156, 165, 196, 1.0)',
            symbol='circle',
            line_width=1.0,
            size=18
        ),
        mode='markers'
    )
    
    fig.add_trace(points_graph)
    fig.update_layout(
        xaxis=dict(
            showgrid=False,
            showline=True,
            linecolor='rgb(102, 102, 102)',
            tickfont_color='rgb(102, 102, 102)',
            showticklabels=True,
            # dtick=10,
            ticks='outside',
            tickcolor='rgb(102, 102, 102)',
    ),
        margin=dict(l=140, r=40, b=50, t=80),
    # legend=dict(
    #     font_size=10,
    #     yanchor='middle',
    #     xanchor='right',
    # ),
        # width=800,
        # height=600,
        paper_bgcolor='white',
        plot_bgcolor='white',
        hovermode='closest',
    )
    
    return fig, 'visible'

    