import networkx as nx
import pandas as pd
from os.path import join as j
from fa2 import ForceAtlas2
from webweb import Web


def layout_network(network: nx.Graph, layout_name: str) -> nx.Graph:
    """
    Apply a specified layout algorithm to a network and return the modified NetworkX graph object.

    The function modifies the positions of the nodes in the graph according to the chosen layout algorithm and returns a new NetworkX graph object with these positions. It supports three layout algorithms: 'fa2' (ForceAtlas2), 'spring', and 'graphviz'.

    Args:
        network (nx.Graph): The NetworkX graph object
        layout_name (str): The name of the layout algorithm to use. Valid options are "fa2", "spring", or "graphviz"

    Returns:
        nx.Graph: A new networkx graph object having the same nodes and edges as the original, but with the positions of the nodes arranged according to the layout algorithm

    Raises:
        ValueError: If `layout_name` is not one of the supported layout algorithms ("fa2", "spring", or "graphviz")
    """

    G_layout = network.copy()
    if layout_name == "fa2":
        forceatlas2 = ForceAtlas2(
            # Behavior alternatives
            outboundAttractionDistribution=True,
            linLogMode=False,
            adjustSizes=False,
            edgeWeightInfluence=1.0,
            # Performance
            jitterTolerance=1.0,
            barnesHutOptimize=True,
            barnesHutTheta=1.2,
            multiThreaded=False,
            # Tuning
            scalingRatio=2.0,
            strongGravityMode=False,
            gravity=1.0,
            # Log
            verbose=True,
        )
        layout_pos = forceatlas2.forceatlas2_networkx_layout(
            G_layout, pos=None, iterations=500
        )
    elif layout_name == "spring":
        layout_pos = nx.spring_layout(G_layout)
    elif layout_name == "graphviz":
        layout_pos = nx.nx_agraph.graphviz_layout(G_layout)
    else:
        raise ValueError(
            "Unsupported layout algorithm. Choose 'fa2', 'spring', or 'graphviz'."
        )

    for node, (x, y) in layout_pos.items():
        G_layout.nodes[node]["x"] = x
        G_layout.nodes[node]["y"] = y
    return G_layout


def layout_metrics(
    original_network: nx.Graph, backbone_network: nx.Graph
) -> pd.DataFrame:
    """
    Compute and return metrics for both the original and backbone networks as a pandas dataframe.

    Metrics include the percentage of nodes in the giant connected component (GCC), the percentage of edges removed, and the percentage of total edge weight removed. These metrics are calculated for both the original and backbone networks and are returned as a Pandas DataFrame.

    Args:
        original_network (nx.Graph): The original NetworkX graph object
        backbone_network (nx.Graph): The backbone NetworkX graph object after using the layout algorithm

    Returns:
        pd.DataFrame: A Pandas DataFrame including information about node percentages, edge removal percentages, and edge weight removal percentages for both the original and backbone networks

    Raises:
        ValueError: If either the original network or the backbone network does not contain edge weights
    """
    if not nx.get_edge_attributes(
        original_network, "weight"
    ) or not nx.get_edge_attributes(backbone_network, "weight"):
        raise ValueError("All edges in the network must have a 'weight' attribute.")

    ## 1. % of nodes in gcc
    if original_network.is_directed():
        original_network_gcc_nodes = max(
            nx.weakly_connected_components(original_network), key=len
        )
    else:
        original_network_gcc_nodes = max(
            nx.connected_components(original_network), key=len
        )

    original_network_gcc = original_network.subgraph(original_network_gcc_nodes)
    original_network_gcc_node_percentage = (
        len(original_network_gcc) / len(original_network)
    ) * 100
    backbone_network_node_percentage = (
        len(backbone_network) / len(original_network)
    ) * 100

    ## 2. % of edges removed
    original_network_edges_count = original_network.number_of_edges()
    original_network_gcc_edges_count = original_network_gcc.number_of_edges()
    backbone_network_edges_count = backbone_network.number_of_edges()
    original_network_gcc_edges_removed_percentage = (
        (original_network_edges_count - original_network_gcc_edges_count)
        / original_network_edges_count
    ) * 100
    backbone_network_edges_removed_percentage = (
        (original_network_edges_count - backbone_network_edges_count)
        / original_network_edges_count
    ) * 100

    ## 3. % of total edge weight removed
    total_weight_original_network = sum(
        w for u, v, w in original_network.edges(data="weight")
    )
    total_weight_original_network_gcc = sum(
        w for u, v, w in original_network_gcc.edges(data="weight")
    )
    total_weight_backbone_network = sum(
        w for u, v, w in backbone_network.edges(data="weight")
    )
    original_network_gcc_edge_weight_removed_percentage = (
        (total_weight_original_network - total_weight_original_network_gcc)
        / total_weight_original_network
    ) * 100
    backbone_network_edge_weight_removed_percentage = (
        (total_weight_original_network - total_weight_backbone_network)
        / total_weight_original_network
    ) * 100

    metrics = {
        "Metric": [
            "Original Network GCC Node",
            "Backbone Network Node",
            "Original Network GCC Edges Removed",
            "Backbone Network Edges Removed",
            "Original Network GCC Edge Weight Removed",
            "Backbone Network Edge Weight Removed",
        ],
        "Percentage": [
            original_network_gcc_node_percentage,
            backbone_network_node_percentage,
            original_network_gcc_edges_removed_percentage,
            backbone_network_edges_removed_percentage,
            original_network_gcc_edge_weight_removed_percentage,
            backbone_network_edge_weight_removed_percentage,
        ],
    }

    return pd.DataFrame(metrics)


def get_webweb(network: nx.Graph, output_dir: str, file_name: str) -> None:
    """
    Generate a webweb dashboard for a given network and save it as an HTML file.
    Since webweb primarily displays node IDs, the network is restructured to use labels.

    Args:
        network (nx.Graph): The NetworkX graph object
        output_dir (str): The directory where the HTML file will be saved
        file_name (str): The name of the HTML file

    Raises:
        ValueError: If any node in the network does not have a 'label' attribute
    """

    label_graph = nx.Graph()
    for node in network.nodes():
        if "label" not in network.nodes[node]:
            raise ValueError(f"Node {node} does not have a 'label' attribute.")
        label = network.nodes[node]["label"]
        label_graph.add_node(label, **network.nodes[node])
    for u, v, data in network.edges(data=True):
        label_u = network.nodes[u]["label"]
        label_v = network.nodes[v]["label"]
        label_graph.add_edge(label_u, label_v, **data)
    web = Web(nx_G=label_graph)
    web.display.scaleLinkWidth = True
    web.display.showNodeNames = True
    web.display.scaleLinkOpacity = True
    web.display.charge = 400
    web.display.colorBy = "degree"
    web.save(j(output_dir, file_name))
