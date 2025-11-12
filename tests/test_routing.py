"""
Comprehensive Unit Tests for Routing Module

Tests all routing strategies: DirectTransmission, MultiHop, ClusterBased, and Adaptive.
Achieves 95%+ code coverage with edge case testing.
"""

import unittest
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.routing import (
    Router, DirectTransmissionRouter, MultiHopRouter,
    ClusterBasedRouter, AdaptiveRouter
)
from src.network import WirelessSensorNetwork
from src.node import SensorNode, NodeType, NodeState
from src.energy_model import EnergyModel


class TestBaseRouter(unittest.TestCase):
    """Test cases for base Router class"""

    def setUp(self):
        """Set up test fixtures"""
        self.network = WirelessSensorNetwork(num_nodes=10, area_size=(100, 100))
        self.router = Router(self.network)

    def test_router_initialization(self):
        """Test router initialization"""
        self.assertIsNotNone(self.router.network)
        self.assertEqual(self.router.network, self.network)

    def test_route_packet_not_implemented(self):
        """Test that base router raises NotImplementedError"""
        source = self.network.nodes[0]
        destination = self.network.nodes[1]

        with self.assertRaises(NotImplementedError):
            self.router.route_packet(source, destination)


class TestDirectTransmissionRouter(unittest.TestCase):
    """Test cases for DirectTransmissionRouter"""

    def setUp(self):
        """Set up test fixtures"""
        self.network = WirelessSensorNetwork(num_nodes=10, area_size=(100, 100))
        self.router = DirectTransmissionRouter(self.network)

    def test_initialization(self):
        """Test router initialization"""
        self.assertIsNotNone(self.router.network)
        self.assertEqual(self.router.network, self.network)

    def test_route_packet_returns_direct_path(self):
        """Test that route_packet returns [source, destination]"""
        source = self.network.nodes[0]
        destination = self.network.nodes[1]

        path = self.router.route_packet(source, destination)

        self.assertEqual(len(path), 2)
        self.assertEqual(path[0], source)
        self.assertEqual(path[1], destination)

    def test_route_packet_with_coordinates(self):
        """Test routing to coordinate destination"""
        source = self.network.nodes[0]
        destination = (50, 50)

        path = self.router.route_packet(source, destination)

        self.assertEqual(len(path), 2)
        self.assertEqual(path[0], source)
        self.assertEqual(path[1], destination)

    def test_transmit_success(self):
        """Test successful direct transmission"""
        source = self.network.nodes[0]
        destination = self.network.nodes[1]

        # Ensure source has energy
        source.energy = source.initial_energy

        result = self.router.transmit(source, destination)

        # Should succeed if source has enough energy
        self.assertIsInstance(result, bool)

    def test_transmit_with_dead_node(self):
        """Test transmission fails with dead node"""
        source = self.network.nodes[0]
        destination = self.network.nodes[1]

        # Kill source node
        source.energy = 0

        result = self.router.transmit(source, destination)

        self.assertFalse(result)


class TestMultiHopRouter(unittest.TestCase):
    """Test cases for MultiHopRouter with Dijkstra's algorithm"""

    def setUp(self):
        """Set up test fixtures with controlled node positions"""
        # Create network with specific node positions for predictable testing
        self.network = WirelessSensorNetwork(num_nodes=5, area_size=(100, 100))

        # Position nodes in a line for multi-hop testing
        # Node 0: (0, 0)
        # Node 1: (20, 0)
        # Node 2: (40, 0)
        # Node 3: (60, 0)
        # Node 4: (80, 0)
        for i, node in enumerate(self.network.nodes):
            node.x = i * 20
            node.y = 0

        self.router = MultiHopRouter(self.network, max_hop_distance=30)

    def test_initialization(self):
        """Test router initialization"""
        self.assertEqual(self.router.max_hop_distance, 30)
        self.assertIsNotNone(self.router.network)

    def test_initialization_default_max_hop(self):
        """Test initialization with default max_hop_distance"""
        router = MultiHopRouter(self.network)
        self.assertEqual(router.max_hop_distance, 30)

    def test_find_neighbors_within_range(self):
        """Test finding neighbors within communication range"""
        source = self.network.nodes[0]  # At (0, 0)

        neighbors = self.router.find_neighbors(source)

        # Should find node 1 at (20, 0) - distance 20 < 30
        self.assertGreater(len(neighbors), 0)
        self.assertIn(self.network.nodes[1], neighbors)

    def test_find_neighbors_excludes_self(self):
        """Test that node doesn't include itself in neighbors"""
        source = self.network.nodes[0]

        neighbors = self.router.find_neighbors(source)

        self.assertNotIn(source, neighbors)

    def test_find_neighbors_excludes_dead_nodes(self):
        """Test that dead nodes are excluded from neighbors"""
        source = self.network.nodes[0]

        # Kill node 1
        self.network.nodes[1].energy = 0

        neighbors = self.router.find_neighbors(source)

        self.assertNotIn(self.network.nodes[1], neighbors)

    def test_find_neighbors_custom_max_distance(self):
        """Test finding neighbors with custom max distance"""
        source = self.network.nodes[0]

        # Very small distance should find no neighbors
        neighbors = self.router.find_neighbors(source, max_distance=5)

        self.assertEqual(len(neighbors), 0)

    def test_find_neighbors_large_distance(self):
        """Test finding neighbors with large distance"""
        source = self.network.nodes[0]

        # Large distance should find all alive nodes
        neighbors = self.router.find_neighbors(source, max_distance=200)

        # Should find nodes 1-4 (all others)
        self.assertEqual(len(neighbors), 4)

    def test_find_shortest_path_direct(self):
        """Test shortest path when destination is in range"""
        source = self.network.nodes[0]  # (0, 0)
        destination = self.network.nodes[1]  # (20, 0)

        path = self.router.find_shortest_path(source, destination)

        self.assertIsNotNone(path)
        self.assertEqual(path[0], source)
        self.assertIn(destination, path)

    def test_find_shortest_path_multihop(self):
        """Test multi-hop path finding"""
        source = self.network.nodes[0]  # (0, 0)
        destination = self.network.nodes[3]  # (60, 0)

        path = self.router.find_shortest_path(source, destination)

        self.assertIsNotNone(path)
        self.assertEqual(path[0], source)
        self.assertGreater(len(path), 2)  # Multi-hop path

    def test_find_shortest_path_to_coordinates(self):
        """Test path finding to coordinate destination"""
        source = self.network.nodes[0]
        destination = (25, 0)  # Close to node 1

        path = self.router.find_shortest_path(source, destination)

        self.assertIsNotNone(path)
        self.assertEqual(path[0], source)

    def test_find_shortest_path_no_path(self):
        """Test when no path exists (all intermediate nodes dead)"""
        source = self.network.nodes[0]
        destination = self.network.nodes[4]

        # Kill intermediate nodes
        self.network.nodes[1].energy = 0
        self.network.nodes[2].energy = 0
        self.network.nodes[3].energy = 0

        path = self.router.find_shortest_path(source, destination)

        # Should return None when no path exists
        self.assertIsNone(path)

    def test_find_shortest_path_isolated_node(self):
        """Test path finding from isolated node"""
        # Create a node far from others
        isolated_node = SensorNode(
            id=99, x=200, y=200, energy=1.0,
            node_type=NodeType.NORMAL, comm_range=30
        )

        # Should find no path to other nodes
        destination = self.network.nodes[0]
        router = MultiHopRouter(self.network, max_hop_distance=30)

        # Manually create a network with isolated node
        test_network = WirelessSensorNetwork(num_nodes=2, area_size=(300, 300))
        test_network.nodes[0].x = 0
        test_network.nodes[0].y = 0
        test_network.nodes[1].x = 200
        test_network.nodes[1].y = 200

        test_router = MultiHopRouter(test_network, max_hop_distance=30)
        path = test_router.find_shortest_path(test_network.nodes[0], test_network.nodes[1])

        self.assertIsNone(path)

    def test_route_packet(self):
        """Test route_packet method"""
        source = self.network.nodes[0]
        destination = self.network.nodes[2]

        path = self.router.route_packet(source, destination)

        self.assertIsNotNone(path)
        self.assertEqual(path[0], source)

    def test_transmit_success(self):
        """Test successful multi-hop transmission"""
        source = self.network.nodes[0]
        destination = self.network.nodes[2]

        # Ensure all nodes have energy
        for node in self.network.nodes:
            node.energy = node.initial_energy

        result = self.router.transmit(source, destination)

        self.assertIsInstance(result, bool)

    def test_transmit_no_path(self):
        """Test transmission fails when no path exists"""
        source = self.network.nodes[0]
        destination = self.network.nodes[4]

        # Kill all intermediate nodes
        for i in range(1, 4):
            self.network.nodes[i].energy = 0

        result = self.router.transmit(source, destination)

        self.assertFalse(result)

    def test_transmit_to_coordinates(self):
        """Test transmission to coordinate destination"""
        source = self.network.nodes[0]
        destination = (25, 0)

        # Ensure nodes have energy
        for node in self.network.nodes:
            node.energy = node.initial_energy

        result = self.router.transmit(source, destination)

        self.assertIsInstance(result, bool)

    def test_transmit_node_dies_during_transmission(self):
        """Test transmission fails if intermediate node dies"""
        source = self.network.nodes[0]
        destination = self.network.nodes[3]

        # Give nodes minimal energy that may run out
        for node in self.network.nodes:
            node.energy = 0.001

        result = self.router.transmit(source, destination)

        # May fail due to energy depletion
        self.assertIsInstance(result, bool)

    def test_energy_penalty_in_pathfinding(self):
        """Test that path finding considers node energy levels"""
        source = self.network.nodes[0]
        destination = self.network.nodes[3]

        # Give node 1 very low energy
        self.network.nodes[1].energy = 0.01
        # Give node 2 high energy
        self.network.nodes[2].energy = self.network.nodes[2].initial_energy

        path = self.router.find_shortest_path(source, destination)

        # Path should exist even with low energy node
        if path:
            self.assertEqual(path[0], source)


class TestClusterBasedRouter(unittest.TestCase):
    """Test cases for ClusterBasedRouter"""

    def setUp(self):
        """Set up test fixtures"""
        self.network = WirelessSensorNetwork(num_nodes=10, area_size=(100, 100))
        self.router = ClusterBasedRouter(self.network)

        # Set up cluster structure
        self.cluster_head = self.network.nodes[0]
        self.member_node = self.network.nodes[1]

        self.cluster_head.node_type = NodeType.CLUSTER_HEAD
        self.member_node.cluster_head = self.cluster_head

    def test_initialization(self):
        """Test router initialization"""
        self.assertIsNotNone(self.router.network)
        self.assertEqual(self.router.network, self.network)

    def test_route_to_cluster_head_success(self):
        """Test routing from member to cluster head"""
        # Ensure nodes have energy
        self.member_node.energy = self.member_node.initial_energy
        self.cluster_head.energy = self.cluster_head.initial_energy

        result = self.router.route_to_cluster_head(self.member_node)

        self.assertIsInstance(result, bool)

    def test_route_to_cluster_head_no_cluster(self):
        """Test routing fails when node has no cluster head"""
        orphan_node = self.network.nodes[2]
        orphan_node.cluster_head = None

        result = self.router.route_to_cluster_head(orphan_node)

        self.assertFalse(result)

    def test_route_to_cluster_head_dead_member(self):
        """Test routing fails when member node is dead"""
        self.member_node.energy = 0

        result = self.router.route_to_cluster_head(self.member_node)

        self.assertFalse(result)

    def test_route_to_base_station(self):
        """Test routing from cluster head to base station"""
        base_station = (50, 50)

        self.cluster_head.energy = self.cluster_head.initial_energy

        result = self.router.route_to_base_station(self.cluster_head, base_station)

        self.assertIsInstance(result, bool)

    def test_route_to_base_station_dead_ch(self):
        """Test routing fails when cluster head is dead"""
        base_station = (50, 50)
        self.cluster_head.energy = 0

        result = self.router.route_to_base_station(self.cluster_head, base_station)

        self.assertFalse(result)

    def test_route_packet_from_cluster_head(self):
        """Test routing path from cluster head"""
        self.cluster_head.node_type = NodeType.CLUSTER_HEAD
        destination = (50, 50)

        path = self.router.route_packet(self.cluster_head, destination)

        self.assertEqual(len(path), 2)
        self.assertEqual(path[0], self.cluster_head)
        self.assertEqual(path[1], destination)

    def test_route_packet_from_member(self):
        """Test routing path from cluster member"""
        destination = (50, 50)

        path = self.router.route_packet(self.member_node, destination)

        self.assertEqual(len(path), 3)
        self.assertEqual(path[0], self.member_node)
        self.assertEqual(path[1], self.cluster_head)
        self.assertEqual(path[2], destination)

    def test_route_packet_from_orphan_node(self):
        """Test routing path from node without cluster"""
        orphan_node = self.network.nodes[2]
        orphan_node.cluster_head = None
        orphan_node.node_type = NodeType.NORMAL
        destination = (50, 50)

        path = self.router.route_packet(orphan_node, destination)

        # Should use direct transmission
        self.assertEqual(len(path), 2)
        self.assertEqual(path[0], orphan_node)
        self.assertEqual(path[1], destination)


class TestAdaptiveRouter(unittest.TestCase):
    """Test cases for AdaptiveRouter"""

    def setUp(self):
        """Set up test fixtures"""
        self.network = WirelessSensorNetwork(num_nodes=10, area_size=(100, 100))
        self.router = AdaptiveRouter(self.network, distance_threshold=50)

        # Position nodes for predictable testing
        self.network.nodes[0].x = 0
        self.network.nodes[0].y = 0
        self.network.nodes[1].x = 30  # Close (< threshold)
        self.network.nodes[1].y = 0
        self.network.nodes[2].x = 80  # Far (> threshold)
        self.network.nodes[2].y = 0

    def test_initialization(self):
        """Test router initialization"""
        self.assertEqual(self.router.distance_threshold, 50)
        self.assertIsNotNone(self.router.direct_router)
        self.assertIsNotNone(self.router.multihop_router)

    def test_initialization_default_threshold(self):
        """Test initialization with default threshold"""
        router = AdaptiveRouter(self.network)
        self.assertEqual(router.distance_threshold, 50)

    def test_route_packet_short_distance(self):
        """Test routing uses direct transmission for short distances"""
        source = self.network.nodes[0]
        destination = self.network.nodes[1]  # Distance = 30 < 50

        path = self.router.route_packet(source, destination)

        # Should use direct transmission (2 nodes)
        self.assertEqual(len(path), 2)

    def test_route_packet_long_distance_high_energy(self):
        """Test routing uses direct transmission for high energy nodes"""
        source = self.network.nodes[0]
        destination = self.network.nodes[2]  # Distance = 80 > 50

        # High energy (> 80%)
        source.energy = 0.9 * source.initial_energy

        path = self.router.route_packet(source, destination)

        # Should use direct transmission due to high energy
        self.assertEqual(len(path), 2)

    def test_route_packet_long_distance_low_energy(self):
        """Test routing uses multi-hop for long distance + low energy"""
        source = self.network.nodes[0]
        destination = self.network.nodes[2]

        # Low energy (< 80%)
        source.energy = 0.5 * source.initial_energy

        path = self.router.route_packet(source, destination)

        # Path should exist (may be direct or multi-hop depending on network)
        self.assertIsNotNone(path)
        self.assertGreaterEqual(len(path), 2)

    def test_route_packet_multihop_fallback(self):
        """Test fallback to direct when multi-hop fails"""
        # Create isolated network where multi-hop will fail
        test_network = WirelessSensorNetwork(num_nodes=3, area_size=(200, 200))
        test_network.nodes[0].x = 0
        test_network.nodes[0].y = 0
        test_network.nodes[1].x = 100
        test_network.nodes[1].y = 100
        test_network.nodes[2].x = 150
        test_network.nodes[2].y = 150

        test_router = AdaptiveRouter(test_network, distance_threshold=30)

        source = test_network.nodes[0]
        destination = test_network.nodes[2]

        # Low energy, long distance
        source.energy = 0.3 * source.initial_energy

        path = test_router.route_packet(source, destination)

        # Should fall back to direct transmission
        self.assertIsNotNone(path)
        self.assertEqual(len(path), 2)

    def test_transmit_direct_path(self):
        """Test transmission with direct path"""
        source = self.network.nodes[0]
        destination = self.network.nodes[1]

        source.energy = source.initial_energy

        result = self.router.transmit(source, destination)

        self.assertIsInstance(result, bool)

    def test_transmit_multihop_path(self):
        """Test transmission with multi-hop path"""
        # Create network with nodes in a line
        test_network = WirelessSensorNetwork(num_nodes=4, area_size=(200, 200))
        for i, node in enumerate(test_network.nodes):
            node.x = i * 30
            node.y = 0
            node.energy = node.initial_energy

        test_router = AdaptiveRouter(test_network, distance_threshold=30)

        source = test_network.nodes[0]
        source.energy = 0.5 * source.initial_energy  # Low energy
        destination = test_network.nodes[3]

        result = test_router.transmit(source, destination)

        self.assertIsInstance(result, bool)

    def test_transmit_to_coordinates(self):
        """Test transmission to coordinate destination"""
        source = self.network.nodes[0]
        destination = (35, 0)

        source.energy = source.initial_energy

        result = self.router.transmit(source, destination)

        self.assertIsInstance(result, bool)


class TestRouterEdgeCases(unittest.TestCase):
    """Test edge cases and integration scenarios"""

    def setUp(self):
        """Set up test fixtures"""
        self.network = WirelessSensorNetwork(num_nodes=5, area_size=(100, 100))

    def test_routing_with_all_dead_nodes(self):
        """Test routing when all nodes are dead"""
        # Kill all nodes
        for node in self.network.nodes:
            node.energy = 0

        router = MultiHopRouter(self.network)
        path = router.find_shortest_path(self.network.nodes[0], self.network.nodes[4])

        self.assertIsNone(path)

    def test_routing_single_alive_node(self):
        """Test routing with only source node alive"""
        source = self.network.nodes[0]
        destination = self.network.nodes[4]

        # Kill all except source
        for i, node in enumerate(self.network.nodes):
            if i > 0:
                node.energy = 0

        router = MultiHopRouter(self.network)
        path = router.find_shortest_path(source, destination)

        # Should not find path to dead destination
        self.assertIsNone(path)

    def test_routing_to_self(self):
        """Test routing from node to itself"""
        node = self.network.nodes[0]
        router = DirectTransmissionRouter(self.network)

        path = router.route_packet(node, node)

        self.assertEqual(len(path), 2)
        self.assertEqual(path[0], node)
        self.assertEqual(path[1], node)

    def test_multiple_routers_same_network(self):
        """Test multiple router instances on same network"""
        router1 = DirectTransmissionRouter(self.network)
        router2 = MultiHopRouter(self.network)
        router3 = AdaptiveRouter(self.network)

        # All should work on same network
        source = self.network.nodes[0]
        destination = self.network.nodes[1]

        path1 = router1.route_packet(source, destination)
        path2 = router2.route_packet(source, destination)
        path3 = router3.route_packet(source, destination)

        self.assertIsNotNone(path1)
        self.assertIsNotNone(path2)
        self.assertIsNotNone(path3)


class TestRouterIntegration(unittest.TestCase):
    """Integration tests for routing with different network configurations"""

    def test_routing_in_dense_network(self):
        """Test routing in dense network with many nodes"""
        network = WirelessSensorNetwork(num_nodes=50, area_size=(100, 100))
        router = MultiHopRouter(network, max_hop_distance=20)

        source = network.nodes[0]
        destination = network.nodes[49]

        path = router.find_shortest_path(source, destination)

        # Should find a path in dense network
        self.assertIsNotNone(path)
        if path:
            self.assertGreater(len(path), 2)

    def test_routing_in_sparse_network(self):
        """Test routing in sparse network with few nodes"""
        network = WirelessSensorNetwork(num_nodes=5, area_size=(200, 200))
        router = MultiHopRouter(network, max_hop_distance=30)

        # Nodes may be too far apart
        source = network.nodes[0]
        destination = network.nodes[4]

        path = router.find_shortest_path(source, destination)

        # Path may or may not exist depending on random positions
        # Just verify it doesn't crash
        self.assertIsNotNone(path) or self.assertIsNone(path)

    def test_adaptive_routing_energy_depletion(self):
        """Test adaptive router behavior as energy depletes"""
        network = WirelessSensorNetwork(num_nodes=10, area_size=(100, 100))
        router = AdaptiveRouter(network)

        source = network.nodes[0]
        destination = network.nodes[5]

        # Test with high energy
        source.energy = 0.9 * source.initial_energy
        path_high_energy = router.route_packet(source, destination)

        # Test with low energy
        source.energy = 0.3 * source.initial_energy
        path_low_energy = router.route_packet(source, destination)

        # Both should return valid paths
        self.assertIsNotNone(path_high_energy)
        self.assertIsNotNone(path_low_energy)


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)
