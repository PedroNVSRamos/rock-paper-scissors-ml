import matplotlib
matplotlib.use('Agg')
import math
import dash
import dash_bootstrap_components as dbc
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import io
import base64

# Entity Class
class Entity:
    def __init__(self, name, type):
        self.name = name
        self.type = type
        self.relations = {}

    def add_relation(self, relation, target):
        if relation not in self.relations:
            self.relations[relation] = []
        if target not in self.relations[relation]:
            self.relations[relation].append(target)

# Load CSVs
relationships = pd.read_csv('relationships.csv')
participants = pd.read_csv('participants.csv')

# Initialize entities from participants.csv
entities = {row['Name']: Entity(row['Name'], row['Type']) for _, row in participants.iterrows()}

# Populate relationships from relationships.csv
for _, row in relationships.iterrows():
    subject_type, relationship, object_type = row['SubjectType'], row['Relationship'], row['ObjectType']
    for entity_name, entity in entities.items():
        if entity.type == subject_type:
            for target_name, target in entities.items():
                if target.type == object_type:
                    entity.add_relation(relationship, target_name)

# Dash App
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

participants_options = [{'label': entity.name, 'value': entity.name} for entity in entities.values()]
relationship_options = list(set([rel for entity in entities.values() for rel in entity.relations]))
relation_types = relationships['RelationType'].unique()

app.layout = dbc.Container([
    html.H1("Relationship Viewer"),
    dbc.Row([
        dbc.Col([
            html.Label("Select Participants:"),
            dcc.Dropdown(id='participants-dropdown', options=participants_options, multi=True, value=list(entities.keys())),
        ], width=4),
        dbc.Col([
            html.Label("Select type of relation:"),
            dcc.Dropdown(id='relation-type-dropdown', options=[{'label': rel_type, 'value': rel_type} for rel_type in relation_types], multi=True),
        ], width=4),
        dbc.Col([
            html.Label("Select Relationships:"),
            dcc.Dropdown(id='relationships-dropdown', multi=True, value=relationship_options),
        ], width=4),
    ]),
    dbc.Row([
        dbc.Col([
            dbc.Button("Run", id="run-btn", color="primary", className="mt-2")
        ], width=2)
    ]),
    dbc.Row([
        dbc.Col([
            html.Img(id='network-graph', className="mt-4")
        ])
    ]),
], fluid=True)

def generate_layout(G):
    pos = nx.spring_layout(G)
    for node, data in G.nodes(data=True):
        if data['type'] == 'Human':
            r = 2
            angle = hash(node) % 360
            pos[node] = (r * math.cos(math.radians(angle)), r * math.sin(math.radians(angle)))
    return pos

@app.callback(
    Output('relationships-dropdown', 'options'),
    Output('relationships-dropdown', 'value'),
    Input('relation-type-dropdown', 'value')
)
def filter_relationships_by_type(selected_relation_type):
    if not selected_relation_type:
        options = [{'label': rel, 'value': rel} for rel in relationship_options]
        return options, []
    filtered_relationships = relationships[relationships['RelationType'].isin(selected_relation_type)]
    available_relations = filtered_relationships['Relationship'].unique()
    options = [{'label': rel, 'value': rel} for rel in available_relations]
    return options, list(available_relations)

@app.callback(
    Output('network-graph', 'src'),
    Input('run-btn', 'n_clicks'),
    Input('participants-dropdown', 'value'),
    Input('relationships-dropdown', 'value')
)
def update_output(n_clicks, selected_participants, selected_relationships):
    if n_clicks is None:
        return dash.no_update

    G = nx.DiGraph()
    color_map = {
        "Human": "red",
        "Food": "yellow",
        "Animal": "blue",
        "Pet": "orange",
        "Toy": "green",
        "Vehicle": "purple"
    }

    for entity_name in selected_participants:
        entity = entities[entity_name]
        G.add_node(entity.name, type=entity.type)

    for entity_name in selected_participants:
        entity = entities[entity_name]
        for relation, targets in entity.relations.items():
            if relation not in selected_relationships:
                continue
            for target in targets:
                if target in selected_participants:
                    G.add_edge(entity.name, target, relation=relation)

    pos = nx.shell_layout(G)  # or any other layout you prefer
    node_colors = [color_map.get(data['type'], "gray") for node, data in G.nodes(data=True)]
    labels = nx.get_edge_attributes(G, 'relation')
    
    non_self_edges = [(u, v) for u, v in G.edges() if u != v]

    # 1. Adjust label position for curved edges.
    # This creates an offset for edge labels. The values can be fine-tuned for best visual result.
    label_pos = {}
    for u, v, data in G.edges(data=True):
        if u != v:  # Only for non-self-edges
            x0, y0 = pos[u]
            x1, y1 = pos[v]
            label_pos[(u, v)] = ((x0 + x1) / 2 + (y1 - y0) * 0.2, (y0 + y1) / 2 + (x0 - x1) * 0.2)

    # 2. Color the labels based on the target node (object) of the edge.
    label_colors = {(u, v): color_map[G.nodes[v]['type']] for u, v in non_self_edges}

    edge_colors = [color_map[G.nodes[v]['type']] for u, v in G.edges() if u != v]

    plt.figure(figsize=(10, 6))
    
    # Draw the nodes and non-self-edges with the specified edge colors and curved arrows
    nx.draw(G, pos, with_labels=True, node_size=2000, node_color=node_colors, font_size=10, width=2, alpha=0.6, edge_color=edge_colors, arrowsize=20, edgelist=non_self_edges, connectionstyle="arc3,rad=0.2")

    # Filter edge labels
    filtered_labels = {(u, v): d for (u, v), d in labels.items() if u != v and u in pos and v in pos}
    
    # Filter the label_colors to match the filtered_labels
    filtered_label_colors = [label_colors[edge] for edge in filtered_labels.keys()]

    for edge, color in zip(filtered_labels.keys(), filtered_label_colors):
        label = filtered_labels[edge]
        x, y = pos[edge[0]]
        x2, y2 = pos[edge[1]]
        x_avg, y_avg = (x + x2) / 2, (y + y2) / 2  # Midpoint of the edge

        plt.text(x_avg, y_avg, label, color=color)

    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)
    base64_image = base64.b64encode(buf.getvalue()).decode('utf-8')

    return "data:image/png;base64,{}".format(base64_image)

if __name__ == "__main__":
    app.run_server(debug=True, port=8050)

if __name__ == "__main__":
    app.run_server(debug=True, port=8050)