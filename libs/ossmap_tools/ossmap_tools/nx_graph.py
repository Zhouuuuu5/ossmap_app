import pandas as pd
import networkx as nx
from typing import Optional
import random


def build_graph(
    edgelist: pd.DataFrame, nodelist: pd.DataFrame, isDirected: Optional[bool] = True
) -> nx.Graph:
    """
    Build a NetworkX graph from given edgelist and nodelist DataFrames.

    Args:
        edgelist (pd.DataFrame): A DataFrame containing the edges of the graph. Must contain columns "Source", "Target", and "weight"
        nodelist (pd.DataFrame): A DataFrame containing the nodes of the graph. Must contain columns "Id", "Label", and "Licenses"
        isDirected (Optional[bool]): A boolean to indicate whether the graph is directed or not. Default is True

    Returns:
        nx.Graph: A NetworkX graph object

    Raises:
        ValueError: If required columns are missing in the edgelist or nodelist DataFrames
    """
    required_columns_nodelist = ["Id", "Label", "Licenses"]
    required_columns_edgelist = ["Source", "Target", "weight"]
    if not all(column in nodelist.columns for column in required_columns_nodelist):
        raise ValueError(
            f"Nodelist DataFrame must contain columns: {required_columns_nodelist}"
        )
    if not all(column in edgelist.columns for column in required_columns_edgelist):
        raise ValueError(
            f"Edgelist DataFrame must contain columns: {required_columns_edgelist}"
        )

    G = nx.DiGraph() if isDirected else nx.Graph()
    nodelist = nodelist.astype({"Id": "int64"})
    cols_to_convert = nodelist.select_dtypes(exclude="int64").columns
    nodelist[cols_to_convert] = nodelist[cols_to_convert].astype(str)
    edgelist = edgelist.astype(
        {"Source": "int64", "Target": "int64", "weight": "float64"}
    )

    for _, row in nodelist.iterrows():
        attributes = {key.lower(): value for key, value in row.to_dict().items()}
        G.add_node(row["Id"], **attributes)

    for _, row in edgelist.iterrows():
        attributes = {key.lower(): value for key, value in row.to_dict().items()}
        G.add_edge(row["Source"], row["Target"], **attributes)
    return G


def build_shuffled_weight_graph(
    edgelist: pd.DataFrame, nodelist: pd.DataFrame, isDirected: Optional[bool] = True
) -> nx.Graph:
    """
    Build a NetworkX graph from given edgelist and nodelist DataFrames with shuffled weights.

    Args:
        edgelist (pd.DataFrame): A DataFrame containing the edges of the graph. Must contain columns "Source", "Target", and "weight"
        nodelist (pd.DataFrame): A DataFrame containing the nodes of the graph. Must contain columns "Id", "Label", and "Licenses"
        isDirected (Optional[bool]): A boolean to indicate whether the graph is directed or not. Default is True

    Returns:
        nx.Graph: A NetworkX graph object

    Raises:
        ValueError: If required columns are missing in the edgelist or nodelist DataFrames
    """
    required_columns_nodelist = ["Id", "Label", "Licenses"]
    required_columns_edgelist = ["Source", "Target", "weight"]
    if not all(column in nodelist.columns for column in required_columns_nodelist):
        raise ValueError(
            f"Nodelist DataFrame must contain columns: {required_columns_nodelist}"
        )
    if not all(column in edgelist.columns for column in required_columns_edgelist):
        raise ValueError(
            f"Edgelist DataFrame must contain columns: {required_columns_edgelist}"
        )

    G = nx.DiGraph() if isDirected else nx.Graph()
    nodelist = nodelist.astype(
        {"Id": "int64", "Label": "str", "Licenses": "str", "Topic": "str"}
    )
    edgelist = edgelist.astype(
        {"Source": "int64", "Target": "int64", "weight": "float64"}
    )

    shuffled_weights = edgelist["weight"].tolist()
    random.shuffle(shuffled_weights)

    for _, row in nodelist.iterrows():
        G.add_node(
            row["Id"], label=row["Label"], licenses=row["Licenses"], topic=row["Topic"]
        )
    for edge, weight in zip(edgelist.itertuples(index=False), shuffled_weights):
        G.add_edge(edge.Source, edge.Target, weight=weight)
    return G


def build_random_weight_graph(
    edgelist: pd.DataFrame, nodelist: pd.DataFrame, isDirected: Optional[bool] = True
) -> nx.Graph:
    """
    Build a NetworkX graph from given edgelist and nodelist DataFrames with random weights.

    Args:
        edgelist (pd.DataFrame): A DataFrame containing the edges of the graph. Must contain columns "Source", "Target", and "weight"
        nodelist (pd.DataFrame): A DataFrame containing the nodes of the graph. Must contain columns "Id", "Label", and "Licenses"
        isDirected (Optional[bool]): A boolean to indicate whether the graph is directed or not. Default is True

    Returns:
        nx.Graph: A NetworkX graph object

    Raises:
        ValueError: If required columns are missing in the edgelist or nodelist DataFrames
    """
    required_columns_nodelist = ["Id", "Label", "Licenses"]
    required_columns_edgelist = ["Source", "Target", "weight"]
    if not all(column in nodelist.columns for column in required_columns_nodelist):
        raise ValueError(
            f"Nodelist DataFrame must contain columns: {required_columns_nodelist}"
        )
    if not all(column in edgelist.columns for column in required_columns_edgelist):
        raise ValueError(
            f"Edgelist DataFrame must contain columns: {required_columns_edgelist}"
        )

    G = nx.DiGraph() if isDirected else nx.Graph()
    nodelist = nodelist.astype(
        {"Id": "int64", "Label": "str", "Licenses": "str", "Topic": "str"}
    )
    edgelist = edgelist.astype(
        {"Source": "int64", "Target": "int64", "weight": "float64"}
    )

    min_weight = edgelist["weight"].min()
    max_weight = edgelist["weight"].max()

    for _, row in nodelist.iterrows():
        G.add_node(
            row["Id"], label=row["Label"], licenses=row["Licenses"], topic=row["Topic"]
        )
    for _, row in edgelist.iterrows():
        random_weight = random.uniform(min_weight, max_weight)
        G.add_edge(row["Source"], row["Target"], weight=random_weight)
    return G
