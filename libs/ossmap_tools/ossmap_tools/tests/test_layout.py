from unittest import TestCase
import networkx as nx
from ossmap_tools.layout import layout_network


class TestLayout(TestCase):
    def setUp(self):
        """
        Setup test network
        """
        self.test_network = nx.Graph()
        self.test_network.add_node(1, Label="Node1", Licenses="L1")
        self.test_network.add_node(2, Label="Node2", Licenses="L2")
        self.test_network.add_node(3, Label="Node3", Licenses="L3")
        self.test_network.add_edge(1, 2, weight=10)
        self.test_network.add_edge(2, 3, weight=50)

    def test_layout_network_fa2(self):
        """
        Test to ensure that the returned graph object has applied the FA2 layout algorithm
        """
        # at the beginning nodes should not have 'x' and 'y' attributes
        for node in self.test_network.nodes(data=True):
            self.assertNotIn("x", node[1])
            self.assertNotIn("y", node[1])

        test_G_layout = layout_network(self.test_network, "fa2")

        # nodes in returned graph should have 'x' and 'y' attributes
        for node in test_G_layout.nodes(data=True):
            self.assertIn("x", node[1])
            self.assertIn("y", node[1])
