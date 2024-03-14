import json

import networkx as nx
import numpy as np
import pandas as pd
from pyvis.network import Network


def nx_to_pyvis(nx_graph:nx.Graph=None):
    
    G_pyvis = Network(
        height="800px",
        width="100%",
        directed=False,
        bgcolor="#222222",
        font_color="#2c3e50"
    )
    G_pyvis.from_nx(nx_graph)
    G_pyvis.show_buttons(filter_=['physics', "layout"])
    G_pyvis.barnes_hut(
        gravity=-4_000,
        central_gravity=0,
        spring_length=200,
        spring_strength=0.009,
        damping=0.025,
        overlap=0.2
    )
    G_data = json.loads(G_pyvis.to_json())
    
    return G_data


def nx_to_pyvis_process(nx_graph:nx.Graph=None):
    
    G_pyvis = Network(
        height="800px",
        width="100%",
        directed=False,
        bgcolor="#222222",
        font_color="#2c3e50"
    )
    
    node_ids = dict(zip(list(nx_graph.nodes()), range(1, nx_graph.number_of_nodes() + 1)))
    for node in nx_graph.nodes(data=True):
        G_pyvis.add_node(
            node_ids[node[0]],
            label=node[1]['label'],
            title=node[1]['title'],
            size=node[1]['size']
        )
    for edge in nx_graph.edges(data=True):
        G_pyvis.add_edge(
            node_ids[edge[0]],
            node_ids[edge[1]],
            weight=edge[2]['weight'],
            # title=edge[2]['title']
        )
    G_pyvis.show_buttons(filter_=['physics', "layout"])
    G_pyvis.barnes_hut(
        gravity=-5_500, # -3.500
        central_gravity=0,
        spring_length=500, # 200
        spring_strength=0.009,
        damping=0.025,
        overlap=0.98 # 0.2
    )
    G_data = json.loads(G_pyvis.to_json())
    
    return G_data, G_pyvis



def filter_kgraph_nx_to_pyvis(df:pd.DataFrame,
                    year:int=None,
                    university:str=None,
                    k_layout:float=None) -> Network:
    df = df.copy()
    G = nx.MultiDiGraph()
    if not year or not university:
        raise TypeError("Both, year and university name, are required.")

    if (year and university):
        query = f"año_concurso == {year} & institucion_patrocinante == '{university}'"
        df = df.query(query)
    # elif year:
    #     query = f"año_concurso == {year}"
    #     df = df.query(query)
    # elif university:
    #     query = f"institucion_patrocinante == '{university}'"
    #     df = df.query(query)
    
    for folio, group in df.groupby('folioproy'):
        project_type = group['instrumento'].unique()[0]
        researches = group['nombre_completo'].unique().tolist()
        inst = group['institucion_patrocinante'].unique().tolist()
        year = group['año_concurso'].unique()[0]
        area = group['area_estudio'].unique()[0]
        calification = group['nota_proyecto'].unique()[0]
        # Agregado de nodos y aristas
        G.add_node(
            folio,
            label=f'{folio}',
            group='Proyectos',
            title=f'Nota: {str(calification)}\nTipo: {str(project_type)}'
        )
        G.add_node(str(year), label=f'{year}', group='Año', title=f'Año proyectos {str(year)}')
        G.add_node(area, label=f'{area}', group='Areas de estudio')
        for u in inst:
            G.add_node(u, label=f'{u}', group='Instituciones')
            G.add_edge(folio, u, label='patrocinado_por')
       
        G.add_edge(folio, str(year), label='año_adjudicacion')
        G.add_edge(folio, area, label='area_estudio', title=f'Área de estudio: {area}')
        
        for researcher in researches:
            G.add_node(researcher, label=f'{researcher}', group='Investigadores')
            G.add_edge(researcher, folio, label='investigador_de')
    
    if not k_layout:
        k_layout = np.divide(1, np.sqrt(G.number_of_nodes()))
    
    pos = nx.spring_layout(G, k=k_layout, iterations=70)
    xs = {k: v[0] for k, v in dict(pos).items()}
    ys = {k: v[1] for k, v in dict(pos).items()}
    nx.set_node_attributes(G, xs, 'x')
    nx.set_node_attributes(G, ys, 'y')
    nx.set_node_attributes(G, 20, 'size')
    
    G_pyvis = Network(
        height="800px",
        width="100%",
        directed=True,
        bgcolor="#222222",
        font_color="#2c3e50"
    )
    G_pyvis.from_nx(G)
    G_pyvis.show_buttons(filter_=['physics', "layout"])
    G_pyvis.barnes_hut(
        gravity=-4_000,
        central_gravity=0,
        spring_length=500,
        spring_strength=0.009,
        damping=0.025,
        overlap=0.6
    )
    G_data = json.loads(G_pyvis.to_json())
    return G_data