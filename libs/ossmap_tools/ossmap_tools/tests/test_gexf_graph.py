from unittest import TestCase
import networkx as nx
import pandas as pd
from ossmap_tools.gexf_graph import build_gexf_graph


class TestGexfGraph(TestCase):
    def setUp(self):
        """
        Setup test dataframes for nodes and edges
        """
        self.test_nodelist_df = pd.DataFrame(
            {
                "Id": [1, 2, 3],
                "Label": ["Node1", "Node2", "Node3"],
                "Licenses": ["L1", "L2", "L3"],
            }
        )

        self.test_edgelist_df = pd.DataFrame(
            {"Source": [1, 2], "Target": [2, 3], "weight": [10, 50]}
        )

    def test_build_gexf_graph_directed(self):
        """
        Test to ensure that a directed graph is created
        """
        test_directed_G = build_gexf_graph(
            self.test_edgelist_df, self.test_nodelist_df, isDirected=True
        )
        self.assertTrue(len(test_directed_G.nodes), 3)
        self.assertTrue(len(test_directed_G.edges), 2)
        self.assertTrue(test_directed_G.is_directed())

    def test_build_gexf_graph_undirected(self):
        """
        Test to ensure that an undirected graph is created
        """
        test_undirected_G = build_gexf_graph(
            self.test_edgelist_df, self.test_nodelist_df, isDirected=False
        )
        self.assertTrue(len(test_undirected_G.nodes), 3)
        self.assertTrue(len(test_undirected_G.edges), 2)
        self.assertFalse(test_undirected_G.is_directed())
