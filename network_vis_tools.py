import plotly.graph_objects as go
import numpy as np


def create_network_figure(
    G, node_size, node_opacity, edge_size, edge_opacity, node_information
):
    degrees = dict(G.degree())
    sorted_nodes = sorted(G.nodes(), key=lambda node: degrees[node], reverse=True)
    node_x = [G.nodes[node]["x"] for node in sorted_nodes]
    node_y = [G.nodes[node]["y"] for node in sorted_nodes]

    node_text_threshold = degrees[sorted_nodes[len(sorted_nodes) // 80 - 1]]
    node_texts = [
        G.nodes[node]["label"] if degrees[node] >= node_text_threshold else ""
        for node in sorted_nodes
    ]

    node_sizes = [np.log10(degrees[node]) * node_size + 1 for node in sorted_nodes]

    node_colors = [np.log10(degrees[node]) for node in sorted_nodes]

    hover_texts = []
    for node in G.nodes():
        text_parts = [f"{G.nodes[node]['label']}<br>degree: {G.degree(node)}"]
        if "License" in node_information:
            license_info = G.nodes[node].get("licenses", "N/A")
            text_parts.append(f"license: {license_info}")
        hover_text = "<br>".join(text_parts)
        hover_texts.append(hover_text)

    node_trace = go.Scatter(
        x=node_x,
        y=node_y,
        mode="markers+text",
        hoverinfo="text",
        hovertext=hover_texts,
        text=node_texts,
        textposition="bottom center",
        textfont=dict(family="Roboto", size=10),
        marker=dict(
            showscale=True,
            color=node_colors,
            size=node_sizes,
            colorscale="Viridis",
            colorbar=dict(
                thickness=15,
                title="Log10 Node Degree",
                xanchor="left",
                titleside="right",
            ),
            line_width=0.1,
        ),
        opacity=node_opacity,
    )

    edge_x = []
    edge_y = []
    for edge in G.edges():
        x0, y0 = G.nodes[edge[0]]["x"], G.nodes[edge[0]]["y"]
        x1, y1 = G.nodes[edge[1]]["x"], G.nodes[edge[1]]["y"]

        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])

    edge_trace = go.Scatter(
        x=edge_x,
        y=edge_y,
        line=dict(width=edge_size, color="#c0c0c0"),
        hoverinfo="none",
        mode="lines",
        opacity=edge_opacity,
    )

    fig = go.Figure(
        data=[edge_trace, node_trace],
        layout=go.Layout(
            showlegend=False,
            hovermode="closest",
            margin=dict(b=5, l=5, r=5, t=5),
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        ),
    )
    return fig
