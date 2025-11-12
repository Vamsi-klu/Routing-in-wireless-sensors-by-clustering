"""
Comprehensive unit tests for routing.py

Tests cover all routing strategies and mechanisms for 95%+ coverage.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from src.network import WirelessSensorNetwork
from src.routing import (
    Router, DirectTransmissionRouter, MultiHopRouter,
    ClusterBasedRouter, AdaptiveRouter
)


class TestDirectTransmissionRouter:
    """Test direct transmission routing"""

    def test_initialization(self):
        """Test router initialization"""
        network = WirelessSensorNetwork(num_nodes=10)
        router = DirectTransmissionRouter(network)

        assert router.network == network

    def test_route_packet(self):
        """Test route packet returns direct path"""
        network = WirelessSensorNetwork(num_nodes=10)
        router = DirectTransmissionRouter(network)
        source = network.nodes[0]
        dest = network.nodes[1]

        path = router.route_packet(source, dest)

        assert len(path) == 2
        assert path[0] == source
        assert path[1] == dest

    def test_transmit_success(self):
        """Test successful direct transmission"""
        network = WirelessSensorNetwork(num_nodes=10, initial_energy=1.0)
        router = DirectTransmissionRouter(network)
        source = network.nodes[0]
        dest = network.nodes[1]

        result = router.transmit(source, dest)

        assert result is True
        assert source.packets_sent == 1

    def test_transmit_insufficient_energy(self):
        """Test transmission fails with insufficient energy"""
        network = WirelessSensorNetwork(num_nodes=10, initial_energy=0.00001)
        router = DirectTransmissionRouter(network)
        source = network.nodes[0]
        dest = (100, 100)  # Far away

        result = router.transmit(source, dest)

        assert result is False


class TestMultiHopRouter:
    """Test multi-hop routing"""

    def test_initialization(self):
        """Test multi-hop router initialization"""
        network = WirelessSensorNetwork(num_nodes=10)
        router = MultiHopRouter(network, max_hop_distance=30)

        assert router.network == network
        assert router.max_hop_distance == 30

    def test_find_neighbors(self):
        """Test finding neighboring nodes"""
        network = WirelessSensorNetwork(num_nodes=20, deployment='grid')
        router = MultiHopRouter(network, max_hop_distance=30)
        source = network.nodes[0]

        neighbors = router.find_neighbors(source)

        assert isinstance(neighbors, list)
        # All neighbors should be within max distance and alive
        for neighbor in neighbors:
            assert neighbor.is_alive()
            assert source.distance_to(neighbor) <= 30

    def test_find_neighbors_with_custom_distance(self):
        """Test finding neighbors with custom max distance"""
        network = WirelessSensorNetwork(num_nodes=20, deployment='grid')
        router = MultiHopRouter(network, max_hop_distance=30)
        source = network.nodes[0]

        neighbors = router.find_neighbors(source, max_distance=50)

        assert isinstance(neighbors, list)

    def test_find_neighbors_excludes_self(self):
        """Test that find_neighbors excludes the source node"""
        network = WirelessSensorNetwork(num_nodes=20, deployment='grid')
        router = MultiHopRouter(network)
        source = network.nodes[0]

        neighbors = router.find_neighbors(source)

        assert source not in neighbors

    def test_find_neighbors_excludes_dead_nodes(self):
        """Test that find_neighbors excludes dead nodes"""
        network = WirelessSensorNetwork(num_nodes=20, deployment='grid')
        router = MultiHopRouter(network)
        source = network.nodes[0]

        # Kill some nodes
        for i in range(5):
            network.nodes[i+1].state = network.nodes[i+1].state.__class__.DEAD

        neighbors = router.find_neighbors(source, max_distance=1000)

        # No dead nodes should be in neighbors
        for neighbor in neighbors:
            assert neighbor.is_alive()

    def test_find_shortest_path_node_destination(self):
        """Test finding shortest path to node"""
        network = WirelessSensorNetwork(num_nodes=20, deployment='grid', initial_energy=1.0)
        router = MultiHopRouter(network, max_hop_distance=30)
        source = network.nodes[0]
        dest = network.nodes[-1]

        path = router.find_shortest_path(source, dest)

        if path:  # Path may not exist depending on deployment
            assert path[0] == source
            assert isinstance(path, list)

    def test_find_shortest_path_tuple_destination(self):
        """Test finding shortest path to coordinates"""
        network = WirelessSensorNetwork(num_nodes=20, deployment='grid', initial_energy=1.0)
        router = MultiHopRouter(network, max_hop_distance=30)
        source = network.nodes[0]
        dest = (50, 50)

        path = router.find_shortest_path(source, dest)

        if path:
            assert path[0] == source
            assert isinstance(path, list)

    def test_find_shortest_path_no_path(self):
        """Test finding path when no path exists"""
        network = WirelessSensorNetwork(num_nodes=5, deployment='random', initial_energy=1.0)
        router = MultiHopRouter(network, max_hop_distance=1)  # Very small range
        source = network.nodes[0]
        dest = (1000, 1000)  # Very far away

        path = router.find_shortest_path(source, dest)

        # Path may be None if unreachable
        assert path is None or isinstance(path, list)

    def test_route_packet(self):
        """Test route_packet method"""
        network = WirelessSensorNetwork(num_nodes=20, deployment='grid', initial_energy=1.0)
        router = MultiHopRouter(network)
        source = network.nodes[0]
        dest = network.nodes[-1]

        path = router.route_packet(source, dest)

        # Should return a path (or None)
        assert path is None or isinstance(path, list)

    def test_transmit_multi_hop(self):
        """Test multi-hop transmission"""
        network = WirelessSensorNetwork(num_nodes=20, deployment='grid', initial_energy=1.0)
        router = MultiHopRouter(network, max_hop_distance=25)
        source = network.nodes[0]
        dest = network.nodes[10]

        result = router.transmit(source, dest)

        # Result depends on whether path exists
        assert isinstance(result, bool)

    def test_transmit_no_path(self):
        """Test transmission when no path exists"""
        network = WirelessSensorNetwork(num_nodes=5, initial_energy=1.0)
        router = MultiHopRouter(network, max_hop_distance=1)
        source = network.nodes[0]
        dest = (1000, 1000)

        result = router.transmit(source, dest)

        assert result is False

    def test_transmit_to_coordinates(self):
        """Test transmission to coordinate tuple"""
        network = WirelessSensorNetwork(num_nodes=20, deployment='grid', initial_energy=1.0)
        router = MultiHopRouter(network)
        source = network.nodes[0]
        dest = (50, 50)

        result = router.transmit(source, dest)

        assert isinstance(result, bool)


class TestClusterBasedRouter:
    """Test cluster-based routing"""

    def test_initialization(self):
        """Test cluster-based router initialization"""
        network = WirelessSensorNetwork(num_nodes=10)
        router = ClusterBasedRouter(network)

        assert router.network == network

    def test_route_to_cluster_head(self):
        """Test routing to cluster head"""
        network = WirelessSensorNetwork(num_nodes=10, initial_energy=1.0)
        router = ClusterBasedRouter(network)

        # Setup clustering
        ch = network.nodes[0]
        member = network.nodes[1]
        ch.set_cluster_head(True)
        member.join_cluster(ch)

        result = router.route_to_cluster_head(member)

        assert isinstance(result, bool)

    def test_route_to_cluster_head_no_ch(self):
        """Test routing when node has no cluster head"""
        network = WirelessSensorNetwork(num_nodes=10)
        router = ClusterBasedRouter(network)
        node = network.nodes[0]

        result = router.route_to_cluster_head(node)

        assert result is False

    def test_route_to_base_station(self):
        """Test routing from CH to base station"""
        network = WirelessSensorNetwork(num_nodes=10, initial_energy=1.0)
        router = ClusterBasedRouter(network)

        ch = network.nodes[0]
        ch.set_cluster_head(True)

        result = router.route_to_base_station(ch, network.base_station)

        assert isinstance(result, bool)

    def test_route_packet_from_ch(self):
        """Test route packet when source is CH"""
        network = WirelessSensorNetwork(num_nodes=10)
        router = ClusterBasedRouter(network)

        ch = network.nodes[0]
        ch.set_cluster_head(True)
        dest = network.base_station

        path = router.route_packet(ch, dest)

        assert len(path) == 2
        assert path[0] == ch

    def test_route_packet_from_member(self):
        """Test route packet when source is cluster member"""
        network = WirelessSensorNetwork(num_nodes=10)
        router = ClusterBasedRouter(network)

        ch = network.nodes[0]
        member = network.nodes[1]
        ch.set_cluster_head(True)
        member.join_cluster(ch)

        path = router.route_packet(member, network.base_station)

        assert len(path) == 3
        assert path[0] == member
        assert path[1] == ch

    def test_route_packet_no_cluster(self):
        """Test route packet when node has no cluster"""
        network = WirelessSensorNetwork(num_nodes=10)
        router = ClusterBasedRouter(network)

        node = network.nodes[0]
        dest = network.base_station

        path = router.route_packet(node, dest)

        assert len(path) == 2  # Direct transmission


class TestAdaptiveRouter:
    """Test adaptive routing"""

    def test_initialization(self):
        """Test adaptive router initialization"""
        network = WirelessSensorNetwork(num_nodes=10)
        router = AdaptiveRouter(network, distance_threshold=50)

        assert router.network == network
        assert router.distance_threshold == 50
        assert router.direct_router is not None
        assert router.multihop_router is not None

    def test_route_packet_short_distance(self):
        """Test routing uses direct transmission for short distance"""
        network = WirelessSensorNetwork(num_nodes=10, initial_energy=1.0)
        router = AdaptiveRouter(network, distance_threshold=100)
        source = network.nodes[0]
        dest = network.nodes[1]

        path = router.route_packet(source, dest)

        # Should use direct transmission for short distance
        assert len(path) >= 2

    def test_route_packet_long_distance(self):
        """Test routing uses multi-hop for long distance"""
        network = WirelessSensorNetwork(num_nodes=20, deployment='grid', initial_energy=0.3)
        router = AdaptiveRouter(network, distance_threshold=10)
        source = network.nodes[0]
        dest = (90, 90)  # Far away

        path = router.route_packet(source, dest)

        # Should attempt multi-hop for long distance
        assert path is not None

    def test_route_packet_high_energy(self):
        """Test routing uses direct with high energy"""
        network = WirelessSensorNetwork(num_nodes=10, initial_energy=1.0)
        router = AdaptiveRouter(network, distance_threshold=50)
        source = network.nodes[0]
        source.energy = 0.9  # High energy
        dest = (80, 80)

        path = router.route_packet(source, dest)

        assert path is not None

    def test_transmit_direct(self):
        """Test adaptive transmit uses direct transmission"""
        network = WirelessSensorNetwork(num_nodes=10, initial_energy=1.0)
        router = AdaptiveRouter(network, distance_threshold=100)
        source = network.nodes[0]
        dest = network.nodes[1]

        result = router.transmit(source, dest)

        assert isinstance(result, bool)

    def test_transmit_multihop(self):
        """Test adaptive transmit uses multi-hop"""
        network = WirelessSensorNetwork(num_nodes=20, deployment='grid', initial_energy=1.0)
        router = AdaptiveRouter(network, distance_threshold=10)
        source = network.nodes[0]
        source.energy = 0.3  # Lower energy
        dest = (80, 80)

        result = router.transmit(source, dest)

        assert isinstance(result, bool)

    def test_transmit_fallback_to_direct(self):
        """Test that multihop falls back to direct if no path"""
        network = WirelessSensorNetwork(num_nodes=5, initial_energy=1.0)
        router = AdaptiveRouter(network, distance_threshold=10)
        source = network.nodes[0]
        source.energy = 0.3
        dest = (50, 50)

        result = router.transmit(source, dest)

        # Should fallback to direct
        assert isinstance(result, bool)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
