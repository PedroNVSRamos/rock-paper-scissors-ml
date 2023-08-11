import os
import pandas as pd
import networkx as nx
from dash import Dash, dcc, html, Input, Output
import plotly.graph_objects as go

def modify_description(row):
    equipped_tier = int(row['EquippedTiers'])
    effect_sizes = row['EffectSize']
    effects = effect_sizes[:equipped_tier]
    num_placeholders = row['EffectDescription'].count('{}')
    if num_placeholders >= len(effects):
        return row['EffectDescription'].format(*effects)
    else:
        # If there's a mismatch, use only the first value from effects.
        return row['EffectDescription'].format(effects[0])

# Load dataframes at the top level
artifacts_df = pd.read_csv("artifacts.csv").dropna(how='all')
heroes_df = pd.read_csv("heroes.csv").dropna(how='all')

def process_data():
    global artifacts_df, heroes_df

    def parse_field(s):
        if not isinstance(s, str):
            return s
        parts = s.strip('{}').split('|')
        return [float(p) if '.' in p else int(p) for p in parts]

    # Parse the EffectSize column before merging.
    artifacts_df['EffectSize'] = artifacts_df['EffectSize'].apply(parse_field)
    
    # Merge the dataframes
    merged_df = pd.merge(heroes_df, artifacts_df, on='ArtifactId', how='inner')
    merged_df['EffectDescription'] = merged_df.apply(modify_description, axis=1)

    return merged_df

app = Dash(__name__)

app.layout = html.Div([
    html.H1("Heroes and Artifacts Relationship"),
    
    html.Div([
        html.Label("Heroes selected:"),
        dcc.Checklist(
            id='hero-selection-checklist',
            options=[{'label': hero, 'value': hero} for hero in heroes_df['HeroId'].unique()],
            value=heroes_df['HeroId'].unique(),
            inline=True
        )
    ]),
    
    html.Div([
        html.Label("Hero level:"),
        dcc.RangeSlider(
            id='hero-level-slider',
            min=1,
            max=15,
            value=[15],
            marks={5: '5', 10: '10', 15: '15'},
            step=1
        )
    ], style={"width": "50%"}),

    html.Div([
        html.Label("Layout selection:"),
        dcc.Dropdown(
            id='layout-selector',
            options=[
                {'label': 'Kamada-Kawai', 'value': 'kamada_kawai'},
                {'label': 'Circular', 'value': 'circular'},
                {'label': 'Shell', 'value': 'shell'},
                {'label': 'Spring (Fruchterman-Reingold)', 'value': 'spring'},
                {'label': 'Spectral', 'value': 'spectral'}
            ],
            value='kamada_kawai',
            style={"width": "50%"}
        ),
    ]),

    html.Button("Render Graph", id="render-button"),
    dcc.Graph(id="network-graph", style={"height": "80vh"})
])

@app.callback(
    Output("network-graph", "figure"),
    [Input("render-button", "n_clicks"), Input('layout-selector', 'value'), Input('hero-level-slider', 'value'), Input('hero-selection-checklist', 'value')]
)
def update_graph(n, layout_type, selected_level, selected_heroes):
    merged_df = process_data()
    
    # Assuming 'HeroLevel' is the name of the column which specifies the hero level
    merged_df = merged_df[merged_df['UnlockLevel'] <= selected_level[0]]
    
    # Filtering based on selected heroes
    merged_df = merged_df[merged_df['HeroId'].isin(selected_heroes)]

    G = nx.Graph()

    for index, row in merged_df.iterrows():
        hero = row['HeroId']
        target = row['TargetId']

        # Add nodes with types
        G.add_node(hero, type="hero")
        G.add_node(target, type=row['TargetType'].lower())

        # Determine edge color
        color = 'green' if row['TargetUser'] == 'Allies' else 'red'

        # Add edges from TargetId to HeroId
        G.add_edge(target, hero, ArtifactId=row['ArtifactId'], color=color, weight=int(row['EquippedTiers']))

    # Generate shell layout positions
    class_targets = [node for node, data in G.nodes(data=True) if data['type'] == 'class']
    other_targets = [node for node, data in G.nodes(data=True) if data['type'] != 'class' and data['type'] != 'hero']
    heroes = [node for node, data in G.nodes(data=True) if data['type'] == 'hero']
    
    shells = [class_targets, other_targets, heroes]
    
    if layout_type == "kamada_kawai":
        pos = nx.kamada_kawai_layout(G)
    elif layout_type == "circular":
        pos = nx.circular_layout(G)
    elif layout_type == "shell":
        classes = [node for node, data in G.nodes(data=True) if data['type'] == 'class']
        heroes = [node for node, data in G.nodes(data=True) if data['type'] == 'hero']
        pos = nx.shell_layout(G, nlist=[classes, heroes])
    elif layout_type == "spring":
        pos = nx.spring_layout(G, k=0.3)
    elif layout_type == "spectral":
        pos = nx.spectral_layout(G)
    else:
        pos = nx.kamada_kawai_layout(G)

    # Node traces with hover text
    node_x, node_y = zip(*pos.values())

    node_hover_texts = []
    for node in G.nodes():
        if G.nodes[node]['type'] == 'artifact':
            description = merged_df[merged_df['ArtifactId'] == node]['EffectDescription'].iloc[0]
            node_hover_texts.append(description)
        else:
            node_hover_texts.append(node)

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers',
        hoverinfo='text',
        marker=dict(
            showscale=False,
            color=list(dict(G.degree).values()),
            size=50,    # Increase to a value that surely covers the images
            opacity=0.2, # Temporarily set opacity for visualization
            line=dict(width=0.5)
        ),
        text=[f"{node}" if G.nodes[node]['type'] != 'artifact' else merged_df[merged_df['ArtifactId']==node]['EffectDescription'].iloc[0] for node in G.nodes()]
    )

    # Edge traces with hover text
    edge_traces = [
        go.Scatter(
            x=[pos[edge[0]][0], pos[edge[1]][0]],
            y=[pos[edge[0]][1], pos[edge[1]][1]],
            line=dict(width=1, color=G[edge[0]][edge[1]]["color"]),
            hoverinfo='text',
            hovertext=merged_df[merged_df['ArtifactId']==G[edge[0]][edge[1]]['ArtifactId']]['EffectDescription'].iloc[0],
            mode='lines'
        ) for edge in G.edges()
    ]

    # Images for nodes and edges
    node_images = [{
        'source': f"assets/{node}.png",
        'xref': "x",
        'yref': "y",
        'x': x,
        'y': y,
        'sizex': 0.1,
        'sizey': 0.1,
        'xanchor': "center",
        'yanchor': "middle"
    } for node, x, y in zip(G.nodes(), node_x, node_y)]

    edge_images = [{
        'source': f"assets/{G[edge[0]][edge[1]].get('ArtifactId', 'default')}.png",
        'xref': "x",
        'yref': "y",
        'x': (pos[edge[0]][0] + pos[edge[1]][0]) / 2,
        'y': (pos[edge[0]][1] + pos[edge[1]][1]) / 2,
        'sizex': 0.1,
        'sizey': 0.1,
        'xanchor': "center",
        'yanchor': "middle"
    } for edge in G.edges()]

    # Calculate the midpoints of the edges
    midpoints_x = [(pos[edge[0]][0] + pos[edge[1]][0]) / 2 for edge in G.edges()]
    midpoints_y = [(pos[edge[0]][1] + pos[edge[1]][1]) / 2 for edge in G.edges()]

    # Extract hover text for the artifact nodes
    artifact_texts = [
        f"<b>{G[edge[0]][edge[1]]['ArtifactId']}</b><br>{merged_df[merged_df['ArtifactId'] == G[edge[0]][edge[1]]['ArtifactId']]['EffectDescription'].iloc[0]}"
        for edge in G.edges()
    ]

    # Scatter trace for the artifact nodes
    artifact_trace = go.Scatter(
        x=midpoints_x,
        y=midpoints_y,
        mode='markers',
        hoverinfo='text',
        marker=dict(
            showscale=False,
            color='rgba(0,0,0,0)',  # making the markers invisible
            size=30,  # large enough to capture hover
            line=dict(width=0.5)
        ),
        text=artifact_texts
    )

    # Create a figure and return
    fig = go.Figure(
        data=edge_traces + [node_trace, artifact_trace],
        layout=go.Layout(
            height=800,
            showlegend=False,
            hovermode='closest',
            margin=dict(b=0, l=0, r=0, t=0),
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            images=node_images + edge_images
        )
    )

    return fig

if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8050)))