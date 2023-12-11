from dash import (
    Dash,
    html,
    dcc,
    Output,
    Input,
    clientside_callback,
    callback,
)
import dash_bootstrap_components as dbc
import networkx as nx
from network_vis_tools import create_network_figure
import pandas as pd
from os.path import join as j

# Initialize the app - incorporate css
app = Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.JOURNAL,
        dbc.icons.FONT_AWESOME,
        "https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap",
    ],
)
server = app.server

# Part 1: Graph filters
color_mode_switch = html.Span(
    [
        dbc.Label(className="fa fa-moon", html_for="color_mode_switch"),
        dbc.Switch(
            id="color_mode_switch",
            value=False,
            className="d-inline-block ms-1",
            persistence=True,
        ),
        dbc.Label(className="fa fa-sun", html_for="color_mode_switch"),
    ]
)
network_switch = html.Div(
    [
        dbc.Tabs(
            [
                dbc.Tab(label="Direct Citation",
                        tab_id="direct_citation_network"),
                dbc.Tab(label="Co-citation", tab_id="cocitation_network"),
            ],
            id="tab",
            active_tab="cocitation_network",
            style={"display": "flex", "fontSize": "0.9em"},
        )
    ],
)
platform_switch = html.Div(
    [
        html.H6("Platform"),
        dbc.RadioItems(
            options=[{"label": x, "value": x.lower()}
                     for x in ["PyPI", "CRAN"]],
            value="pypi",
            inline=True,
            id="platform",
            style={"fontSize": "0.9em"},
        ),
    ]
)
size_of_nodes = html.Div(
    # Options to change appearance of nodes and edges
    [
        html.H6("Size of Nodes"),
        dcc.Slider(
            10,
            50,
            value=10,
            marks=None,
            id="size_of_nodes",
            tooltip={
                "placement": "bottom",
                "always_visible": True,
            },
        ),
    ]
)
opacity_of_nodes = html.Div(
    [
        html.H6("Opacity of Nodes"),
        dcc.Slider(
            0,
            1,
            value=1.0,
            marks=None,
            id="opacity_of_nodes",
            tooltip={
                "placement": "bottom",
                "always_visible": True,
            },
        ),
    ]
)
size_of_edges = html.Div(
    [
        html.H6("Size of Edges"),
        dcc.Slider(
            0,
            1,
            value=0.5,
            marks=None,
            id="size_of_edges",
            tooltip={
                "placement": "bottom",
                "always_visible": True,
            },
        ),
    ]
)
opacity_of_edges = html.Div(
    [
        html.H6("Opacity of Edges"),
        dcc.Slider(
            0,
            1,
            value=0.5,
            marks=None,
            id="opacity_of_edges",
            tooltip={
                "placement": "bottom",
                "always_visible": True,
            },
        ),
    ]
)
label_information = html.Div(
    [
        html.H6("Label Infomation"),
        dcc.Dropdown(
            ["License"],
            "License",
            multi=True,
            id="label_information",
        ),
    ]
)
mst_disparity_slider = html.Div(
    [
        html.H6("MST and Disparity Filter"),
        dcc.Slider(
            min=0.1,
            max=0.7,
            step=0.1,
            value=0.7,
            marks=None,
            tooltip={
                "placement": "bottom",
                "always_visible": True,
            },
            id="mst_disparity_slider_value",
        ),
    ],
    id="mst_disparity_slider_container",
)

graph_filters = dbc.Card(
    dbc.CardBody(
        html.Div(
            [
                color_mode_switch,
                network_switch,
                platform_switch,
                size_of_nodes,
                opacity_of_nodes,
                size_of_edges,
                opacity_of_edges,
                label_information,
                mst_disparity_slider,
            ],
            className="filter-component",
        ),
        style={"margin": "5px"},
    )
)


# Part 2: OSS map
oss_map = html.Div(
    dcc.Graph(
        figure={},
        id="fa2_layout_mst_and_disparity_filter",
        style={
            "width": "100%",
            "height": "90vh",
        },
    ),
)

# Part 3: Summary sidebar
network_metric = html.Div(id="table-container", style={"fontSize": "0.8em"})
node_information = html.Div(id="node-information")
summary_sidebar = html.Div(
    [
        html.Div(network_metric),
        html.Hr(),
        html.Div([html.H6("Node Information"), node_information]),
    ],
    style={"margin": "10px"},
)


# App layout
app.layout = dbc.Container(
    [
        html.Div(
            ["Map of Open Source Software Ecosystem"],
            className="bg-primary text-white h3 p-2",
            style={"textAlign": "center"},
        ),
        dbc.Row(
            [
                dbc.Col(
                    graph_filters,
                    xs=12,
                    sm=12,
                    md=2,
                    lg=2,
                    xl=2,
                    xxl=2,
                ),
                dbc.Col(dcc.Loading(oss_map), xs=12,
                        sm=12, md=8, lg=8, xl=8, xxl=8),
                dbc.Col(
                    summary_sidebar,
                    id="summary_sidebar",
                    xs=12,
                    sm=12,
                    md=2,
                    lg=2,
                    xl=2,
                    xxl=2,
                ),
            ]
        ),
    ],
    fluid=True,
)


# Add controls to build the interaction
@callback(Output("mst_disparity_slider_container", "style"), Input("tab", "active_tab"))
def toggle_slider_visibility(tab):
    if tab == "cocitation_network":
        return {"display": "block"}
    else:
        return {"display": "none"}


@callback(
    Output("fa2_layout_mst_and_disparity_filter", "figure"),
    Input("tab", "active_tab"),
    Input("platform", "value"),
    Input("mst_disparity_slider_value", "value"),
    Input("size_of_nodes", "value"),
    Input("opacity_of_nodes", "value"),
    Input("size_of_edges", "value"),
    Input("opacity_of_edges", "value"),
    Input("label_information", "value"),
    Input("color_mode_switch", "value"),
)
# Use the stored data and user-selected parameters to create graphs
def load_graph(
    tab,
    platform,
    mst_alpha,
    node_size,
    node_opacity,
    edge_size,
    edge_opacity,
    label_information,
    switch_on,
):
    if tab == "cocitation_network":
        file = f"cocitation_network_fa2_layout_{platform}_maximum_spanning_tree_and_disparity_{mst_alpha}.gexf"
    else:
        file = f"direct_citation_network_fa2_layout_{platform}_degree_20.gexf"

    network_data = nx.read_gexf(j("data", file))
    fig = create_network_figure(
        network_data,
        node_size,
        node_opacity,
        edge_size,
        edge_opacity,
        label_information,
    )
    template = "plotly" if switch_on else "plotly_dark"
    fig.layout.template = template
    return fig


@callback(
    Output("table-container", "children"),
    Input("tab", "active_tab"),
    Input("platform", "value"),
    Input("mst_disparity_slider_value", "value"),
)
def update_table(tab, platform, mst_alpha):
    if tab == "cocitation_network":
        csv_file = f"cocitation_network_metrics_{platform}_maximum_spanning_tree_and_disparity_{mst_alpha}.csv"
    else:
        csv_file = f"direct_citation_network_metrics_{platform}_degree_20.csv"
    df = pd.read_csv(j("data", csv_file))
    df = df.round(2)
    table = dbc.Table.from_dataframe(
        df, striped=True, bordered=True, hover=True)
    return table


@app.callback(
    Output("node-information", "children"),
    Input("fa2_layout_mst_and_disparity_filter", "hoverData"),
)
def update_node_information(hoverData):
    if hoverData and "points" in hoverData:
        hover_info = hoverData["points"][0]["hovertext"].split("<br>")
        return html.Div([html.P(line) for line in hover_info])
    return html.Div()


clientside_callback(
    """
    (switchOn) => {
        if (switchOn) {
            document.documentElement.setAttribute('data-bs-theme', 'light');
            document.getElementById('summary_sidebar').style.backgroundColor = '#f3f3f1';
        } else {
            document.documentElement.setAttribute('data-bs-theme', 'dark');
            document.getElementById('summary_sidebar').style.backgroundColor = '';
        }
        return window.dash_clientside.no_update;
    }
    """,
    Output("color_mode_switch", "id"),
    Output("summary_sidebar", "style"),
    Input("color_mode_switch", "value"),
)

if __name__ == "__main__":
    server.run(host='0.0.0.0', port='80')
