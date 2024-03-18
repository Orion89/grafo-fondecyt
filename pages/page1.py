from ast import literal_eval
import json

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
    path='/',
    name='Grafo proyectos',
    title='Grafo de proyectos',
    description='Grafo de conocimiento de proyectos Fondecyt'
)

df = pd.read_csv('./data/proyectos_fondecyt_2012-2019.csv')

layout = html.Div(
    [
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.P("Seleccionar la universiadad y año de en la parte inferior del grafo", className='mb-0 text-secondary'),
                        html.P("Para más información, pasar el puntero sobre cada nodo.", className='mb-0 text-secondary'),
                        html.P("Zoom usando el scrool del ratón.", className='text-secondary')
                    ],
                    width={
                        'size': 6,
                        'offset': 0
                    },
                    align="end"
                ),
                dbc.Col(
                    [
                        dbc.Card(
                            [
                                dbc.CardImg(src='./static/Logo-Fondecyt-1.png', top=True, style={'max-width': '250px'}),
                                dbc.CardBody(
                                    [
                                      html.H3("Red de Conocimiento Científico", className='card-title'),
                                      html.P("Conexiones entre investigadores, proyectos Fondecyt, áreas de estudio y universidades", className='card-text')  
                                    ]
                                )
                            ]
                        )
                    ],
                    width={'size': 6}
                )    
            ],
            class_name='mb-2 mt-3'
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Spinner(
                            html.Div(
                                # network,
                                id='network-1',
                                className='border-2 border-top border-primary'
                            ),
                            color='info'
                        )
                    ],
                    width=12,
                    class_name='mb-1'
                )
            ],
            class_name='mb-3 mt-1'
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
                        'size': 5,
                        'offset': 1
                    },
                    class_name='mb-3'
                ),
                dbc.Col(
                    [
                        dcc.Slider(
                            min=int(df['año_concurso'].min()),
                            max=int(df['año_concurso'].max()),
                            step=None,
                            value=2019,
                            included=False,
                            marks={int(year): str(year) for year in df['año_concurso'].unique()},
                            id='slider-1'
                    )
                    ],
                    width={
                        'size': 5
                    },
                    class_name='mb-3'
                )
            ],
            justify='around',
            class_name='mb-3 border-2 border-bottom border-primary '
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.Div(
                            [
                                html.H4(id='title-treemap-1', className='mb-1 text-center text-primary'),
                                dcc.Graph(id='treemap-1', className='mt-0', config={'displayModeBar': False})
                            ]
                        )
                    ],
                    width={'size': 6},
                    align="center"
                ),
                dbc.Col(
                    [
                        html.Div(
                            [
                                html.H4('Proporción por tipo de proyecto', className='mb-1 text-center text-primary'),
                                dcc.Graph(id='donut-1', config={'displayModeBar': False})
                            ]
                        )
                    ],
                    width={'size': 6}
                )
            ],
            class_name='mt-3 mb-1',
            justify='evenly'
        )
    ]
)

@callback(
    Output('network-1', 'children'),
    Input('dropdown-1', 'value'),
    Input('slider-1', 'value')
)
def create_network(u_name, year):
    G_data = filter_kgraph_nx_to_pyvis(df=df, year=year, university=u_name, k_layout=0.4)
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


@callback(
    Output('treemap-1', 'figure'),
    Output('title-treemap-1', 'children'),
    Input('dropdown-1', 'value')
)
def update_treemap_1(u_name):
    df_filtered = (df[df.institucion_patrocinante == u_name]['area_estudio']
               .value_counts()
               .to_frame()
               .reset_index()
               .rename({'count': 'frecuencia'}, axis=1)
               .copy())
    
    fig = px.treemap(
        df_filtered,
        path=[px.Constant('Áreas'), 'area_estudio'],
        values='frecuencia',
        color_discrete_sequence=px.colors.sequential.Blues_r
    )
    fig.update_traces(root_color="lightgrey")
    fig.update_traces(
        textinfo='label+percent entry',
        insidetextfont=dict(
            # color='black',
            family='Opens Sans, Arial',
            size=16
        )
    )
    fig.update_layout(margin=dict(t=20, l=25, r=25, b=25))
    
    title = f'Mapa de las Prioridades de Investigación de la {u_name}'
    
    return fig, title


@callback(
    Output('donut-1', 'figure'),
    Input('dropdown-1', 'value')
)
def update_donut_1(u_name):
    df_filtered = (df[df.institucion_patrocinante == u_name]['instrumento']
               .value_counts()
               .to_frame()
               .reset_index()
               .rename({'instrumento': 'Tipo de instrumento','count': 'frecuencia'}, axis=1)
               .copy())
    
    fig = px.pie(
        data_frame=df_filtered,
        names='Tipo de instrumento',
        values='frecuencia',
        color_discrete_sequence=px.colors.sequential.Blues_r,
        hole=0.5
    )
    fig.update_traces(
        textposition='outside',
        textinfo='percent+label',
        texttemplate="%{label}<br>%{percent:.1%}",
        textfont={'size':16}
    )
    fig.update_layout(showlegend=False)

    return fig