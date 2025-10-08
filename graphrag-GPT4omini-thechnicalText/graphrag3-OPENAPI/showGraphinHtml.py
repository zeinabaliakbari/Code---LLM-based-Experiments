import os
import re
import json
import subprocess
import pandas as pd
import streamlit as st
import networkx as nx
from pyvis.network import Network

# Message classes

def read_parquet_files():
    nodes_file = ("output/20240718-143114/artifacts/create_final_nodes.parquet")
    relationships_file =("output/20240718-143114/artifacts/create_final_relationships.parquet")
    nodes_df = pd.read_parquet(nodes_file)
    relationships_df = pd.read_parquet(relationships_file)

    print("Nodes DataFrame columns:", nodes_df.columns)  # Debug statement
    print("Relationships DataFrame columns:", relationships_df.columns)  # Debug statement

    return nodes_df, relationships_df

# Function to create a graph from the DataFrames
def create_graph(nodes_df, relationships_df):
    graph = nx.Graph()

    # Adjust the column names based on your DataFrame structure
    node_id_col = 'id'  # Corrected node id column name
    node_label_col = 'title'  # Corrected node label column name
    source_id_col = 'source'  # Corrected source id column name
    target_id_col = 'target'  # Corrected target id column name
    edge_label_col = 'description'  # Corrected edge label column name

    # Add nodes to the graph
    for _, row in nodes_df.iterrows():
        graph.add_node(row[node_id_col], label=row[node_label_col])

    # Add edges to the graph
    for _, row in relationships_df.iterrows():
        graph.add_edge(row[source_id_col], row[target_id_col], label=row[edge_label_col])

    return graph

# Function to visualize the graph using pyvis with dynamic resizing and interactivity
def visualize_graph(graph):
    net = Network(notebook=True, width="100%", height="750px", bgcolor="#222222", font_color="white")
    net.from_nx(graph)

    # Add dynamic resizing and other interactivity options
    options = {
        "nodes": {
            "shape": "dot",
            "size": 10,
            "font": {"size": 16}
        },
        "edges": {
            "color": {"inherit": "from"},
            "smooth": {"type": "dynamic"}
        },
        "physics": {
            "enabled": True,
            "barnesHut": {
                "gravitationalConstant": -8000,
                "centralGravity": 0.3,
                "springLength": 95,
                "springConstant": 0.04,
                "damping": 0.09
            },
            "minVelocity": 0.75
        },
        "interaction": {
            "hover": True,
            "tooltipDelay": 200,
            "hideEdgesOnDrag": True,
            "hideNodesOnDrag": True
        }
    }

    net.set_options(json.dumps(options))
    net.show("graph.html")
    st.write("### Interactive Graph")
    st.components.v1.html(open("graph.html", "r").read(), height=800)

# Streamlit UI for uploading and processing text file


if __name__ == "__main__":
        nodes_df, relationships_df = read_parquet_files()
        graph = create_graph(nodes_df, relationships_df)
        visualize_graph(graph)