from ast import literal_eval
import json

import plotly.graph_objects as go
import plotly.express as px
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
    external_stylesheets=[dbc.themes.FLATLY, stylesheets.VIS_NETWORK_STYLESHEET, dbc.icons.BOOTSTRAP],
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
                        html.P("Seleccionar la universiadad y año de interés en la parte inferior del grafo", className='mb-0'),
                        html.P("Puedes obtener más información al pasar el puntero sobre cada nodo o arrastrarlos manteniendo presionado y moviendo algún nodo en particular.", className='mb-0'),
                        html.P("También puedes hacer zoom usando el scrool del ratón.")
                    ],
                    width={
                        'size': 5,
                        'offset': 1
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
                                      html.H3("Grafo de conocimiento proyectos Fondecyt", className='card-title'),
                                      html.P("Conexiones entre investigadores, proyectos, áreas de estudio y universidades", className='card-text')  
                                    ]
                                )
                            ]
                        )
                    ]
                )    
            ],
            class_name='mb-2 mt-2'
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Container(
                            # network,
                            id='network-1',
                            class_name='border-2 border-top border-bottom border-primary'
                        )
                    ],
                    width=12,
                    class_name='mb-1'
                )
            ],
            class_name='mb-2 mt-1'
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
                    }
                ),
                dbc.Col(
                    dcc.Slider(
                        min=int(df['año_concurso'].min()),
                        max=int(df['año_concurso'].max()),
                        step=None,
                        value=2019,
                        included=False,
                        marks={int(year): str(year) for year in df['año_concurso'].unique()},
                        id='slider-1'
                    ),
                    width={
                        'size': 5
                    }
                )
            ],
            justify='around',
            class_name='mb-3'
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.Div(
                            [
                                html.H4(id='title-treemap-1', className='mb-1 text-center text-primary'),
                                dcc.Graph(id='treemap-1', className='mt-0')
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
                                dcc.Graph(id='donut-1')
                            ]
                        )
                    ],
                    width={'size': 6}
                )
            ],
            class_name='mt-3 mb-1',
            justify='evenly'
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
                                            " ",
                                            html.A(
                                                children=[html.I(className="bi bi-linkedin")],
                                                disable_n_clicks=True,
                                                href='https://www.linkedin.com/in/leonardo-molina-v-68a601183/',
                                                title="LinkedIn profile"
                                            ),
                                            " 2023 Leonardo Molina V."
                                            ]
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


@app.callback(
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
    print(df_filtered.columns)
    
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


@app.callback(
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

if __name__ == "__main__":
    app.run_server(debug=True, port="9000")