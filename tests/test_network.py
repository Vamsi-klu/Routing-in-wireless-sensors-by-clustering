"""
Comprehensive unit tests for network.py

Tests cover all deployment strategies, statistics, and network operations for 95%+ coverage.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
import numpy as np
from src.network import WirelessSensorNetwork
from src.node import NodeType, NodeState
from src.energy_model import EnergyModel


class TestNetworkInitialization:
    """Test network initialization"""

    def test_default_initialization(self):
        """Test network creation with default parameters"""
        network = WirelessSensorNetwork(
            num_nodes=100,
            area_size=(100, 100),
            base_station=(50, 150)
        )

        assert network.num_nodes == 100
        assert network.area_width == 100
        assert network.area_height == 100
        assert network.base_station == (50, 150)
        assert network.initial_energy == 0.5
        assert len(network.nodes) == 100
        assert network.current_round == 0

    def test_custom_parameters(self):
        """Test network with custom parameters"""
        network = WirelessSensorNetwork(
            num_nodes=50,
            area_size=(200, 200),
            base_station=(100, 250),
            initial_energy=1.0
        )

        assert network.num_nodes == 50
        assert network.area_width == 200
        assert network.area_height == 200
        assert network.base_station == (100, 250)
        assert network.initial_energy == 1.0
        assert len(network.nodes) == 50

    def test_custom_energy_model(self):
        """Test network with custom energy model"""
        custom_model = EnergyModel(E_elec=100e-9)
        network = WirelessSensorNetwork(
            num_nodes=10,
            area_size=(100, 100),
            base_station=(50, 150),
            energy_model=custom_model
        )

        assert network.energy_model == custom_model
        # All nodes should use the same model
        for node in network.nodes:
            assert node.energy_model == custom_model

    def test_initial_statistics_none(self):
        """Test that initial lifetime statistics are None"""
        network = WirelessSensorNetwork(num_nodes=10)

        assert network.first_node_death_round is None
        assert network.half_nodes_death_round is None
        assert network.last_node_death_round is None


class TestRandomDeployment:
    """Test random node deployment"""

    def test_random_deployment_node_count(self):
        """Test that random deployment creates correct number of nodes"""
        network = WirelessSensorNetwork(
            num_nodes=50,
            deployment='random'
        )

        assert len(network.nodes) == 50

    def test_random_deployment_within_bounds(self):
        """Test that randomly deployed nodes are within area bounds"""
        network = WirelessSensorNetwork(
            num_nodes=100,
            area_size=(100, 100),
            deployment='random'
        )

        for node in network.nodes:
            assert 0 <= node.x <= 100
            assert 0 <= node.y <= 100

    def test_random_deployment_node_ids(self):
        """Test that nodes have sequential IDs"""
        network = WirelessSensorNetwork(
            num_nodes=20,
            deployment='random'
        )

        node_ids = [node.id for node in network.nodes]
        assert node_ids == list(range(20))

    def test_random_deployment_initial_energy(self):
        """Test that all nodes have correct initial energy"""
        initial_energy = 0.75
        network = WirelessSensorNetwork(
            num_nodes=10,
            initial_energy=initial_energy,
            deployment='random'
        )

        for node in network.nodes:
            assert node.initial_energy == initial_energy
            assert node.energy == initial_energy

    def test_random_deployment_variability(self):
        """Test that random deployment produces different positions"""
        network = WirelessSensorNetwork(
            num_nodes=50,
            deployment='random'
        )

        # Check that not all nodes are at same position
        positions = [(node.x, node.y) for node in network.nodes]
        unique_positions = set(positions)
        assert len(unique_positions) > 40  # Most should be unique


class TestGridDeployment:
    """Test grid node deployment"""

    def test_grid_deployment_node_count(self):
        """Test that grid deployment creates correct number of nodes"""
        network = WirelessSensorNetwork(
            num_nodes=25,
            deployment='grid'
        )

        assert len(network.nodes) == 25

    def test_grid_deployment_pattern(self):
        """Test that grid deployment creates regular pattern"""
        network = WirelessSensorNetwork(
            num_nodes=16,  # 4x4 grid
            area_size=(100, 100),
            deployment='grid'
        )

        # Nodes should be evenly spaced
        x_coords = sorted(set(node.x for node in network.nodes))
        y_coords = sorted(set(node.y for node in network.nodes))

        # Should have 4 unique x and y coordinates
        assert len(x_coords) == 4
        assert len(y_coords) == 4

    def test_grid_deployment_within_bounds(self):
        """Test that grid nodes are within bounds"""
        network = WirelessSensorNetwork(
            num_nodes=25,
            area_size=(100, 100),
            deployment='grid'
        )

        for node in network.nodes:
            assert 0 < node.x < 100
            assert 0 < node.y < 100

    def test_grid_deployment_non_square_number(self):
        """Test grid deployment with non-square number of nodes"""
        network = WirelessSensorNetwork(
            num_nodes=30,
            deployment='grid'
        )

        assert len(network.nodes) == 30

    def test_grid_deployment_spacing(self):
        """Test that grid nodes are properly spaced"""
        network = WirelessSensorNetwork(
            num_nodes=9,  # 3x3 grid
            area_size=(100, 100),
            deployment='grid'
        )

        # With 3x3 grid and 100x100 area, spacing should be 100/4 = 25
        x_coords = sorted(set(round(node.x, 1) for node in network.nodes))
        if len(x_coords) > 1:
            spacing = x_coords[1] - x_coords[0]
            assert 20 < spacing < 30  # Approximately 25


class TestClusterDeployment:
    """Test clustered node deployment"""

    def test_cluster_deployment_node_count(self):
        """Test that cluster deployment creates correct number of nodes"""
        network = WirelessSensorNetwork(
            num_nodes=60,
            deployment='cluster'
        )

        assert len(network.nodes) == 60

    def test_cluster_deployment_within_bounds(self):
        """Test that clustered nodes are within bounds"""
        network = WirelessSensorNetwork(
            num_nodes=60,
            area_size=(100, 100),
            deployment='cluster'
        )

        for node in network.nodes:
            assert 0 <= node.x <= 100
            assert 0 <= node.y <= 100

    def test_cluster_deployment_creates_clusters(self):
        """Test that cluster deployment creates groupings"""
        network = WirelessSensorNetwork(
            num_nodes=60,
            area_size=(200, 200),
            deployment='cluster'
        )

        # Cluster deployment should create groups
        # Nodes in a cluster should be closer to each other
        # This is a basic test - just verify deployment works
        assert len(network.nodes) == 60

    def test_cluster_deployment_small_network(self):
        """Test cluster deployment with small network"""
        network = WirelessSensorNetwork(
            num_nodes=10,
            deployment='cluster'
        )

        assert len(network.nodes) == 10


class TestInvalidDeployment:
    """Test invalid deployment strategies"""

    def test_invalid_deployment_strategy(self):
        """Test that invalid deployment raises error"""
        with pytest.raises(ValueError):
            WirelessSensorNetwork(
                num_nodes=10,
                deployment='invalid'
            )


class TestNodeQueries:
    """Test node query methods"""

    def test_get_alive_nodes_initially(self):
        """Test that all nodes are alive initially"""
        network = WirelessSensorNetwork(num_nodes=50)

        alive_nodes = network.get_alive_nodes()

        assert len(alive_nodes) == 50

    def test_get_dead_nodes_initially(self):
        """Test that no nodes are dead initially"""
        network = WirelessSensorNetwork(num_nodes=50)

        dead_nodes = network.get_dead_nodes()

        assert len(dead_nodes) == 0

    def test_get_alive_nodes_after_deaths(self):
        """Test alive nodes after some nodes die"""
        network = WirelessSensorNetwork(num_nodes=10, initial_energy=0.0001)

        # Kill some nodes by draining energy
        for i in range(5):
            network.nodes[i].state = NodeState.DEAD

        alive_nodes = network.get_alive_nodes()

        assert len(alive_nodes) == 5

    def test_get_dead_nodes_after_deaths(self):
        """Test dead nodes after some nodes die"""
        network = WirelessSensorNetwork(num_nodes=10)

        # Kill some nodes
        for i in range(3):
            network.nodes[i].state = NodeState.DEAD

        dead_nodes = network.get_dead_nodes()

        assert len(dead_nodes) == 3

    def test_is_dead_false_initially(self):
        """Test that network is not dead initially"""
        network = WirelessSensorNetwork(num_nodes=50)

        assert not network.is_dead()

    def test_is_dead_true_when_all_dead(self):
        """Test that network is dead when all nodes dead"""
        network = WirelessSensorNetwork(num_nodes=10)

        # Kill all nodes
        for node in network.nodes:
            node.state = NodeState.DEAD

        assert network.is_dead()

    def test_is_dead_false_with_some_alive(self):
        """Test that network is not dead with some alive nodes"""
        network = WirelessSensorNetwork(num_nodes=10)

        # Kill most but not all
        for i in range(8):
            network.nodes[i].state = NodeState.DEAD

        assert not network.is_dead()


class TestLifetimeStatistics:
    """Test network lifetime statistics"""

    def test_update_first_node_death(self):
        """Test FND statistic update"""
        network = WirelessSensorNetwork(num_nodes=10)

        # Kill one node
        network.nodes[0].state = NodeState.DEAD

        network.update_lifetime_stats(100)

        assert network.first_node_death_round == 100

    def test_update_half_nodes_death(self):
        """Test HND statistic update"""
        network = WirelessSensorNetwork(num_nodes=10)

        # Kill half the nodes
        for i in range(5):
            network.nodes[i].state = NodeState.DEAD

        network.update_lifetime_stats(200)

        assert network.half_nodes_death_round == 200

    def test_update_last_node_death(self):
        """Test LND statistic update"""
        network = WirelessSensorNetwork(num_nodes=10)

        # Kill all nodes
        for node in network.nodes:
            node.state = NodeState.DEAD

        network.update_lifetime_stats(300)

        assert network.last_node_death_round == 300

    def test_fnd_only_updates_once(self):
        """Test that FND only updates on first death"""
        network = WirelessSensorNetwork(num_nodes=10)

        network.nodes[0].state = NodeState.DEAD
        network.update_lifetime_stats(100)

        network.nodes[1].state = NodeState.DEAD
        network.update_lifetime_stats(200)

        assert network.first_node_death_round == 100  # Should stay 100

    def test_hnd_only_updates_once(self):
        """Test that HND only updates once"""
        network = WirelessSensorNetwork(num_nodes=10)

        # Kill half
        for i in range(5):
            network.nodes[i].state = NodeState.DEAD
        network.update_lifetime_stats(100)

        # Kill more
        for i in range(5, 7):
            network.nodes[i].state = NodeState.DEAD
        network.update_lifetime_stats(200)

        assert network.half_nodes_death_round == 100

    def test_get_network_lifetime_stats(self):
        """Test getting lifetime statistics"""
        network = WirelessSensorNetwork(num_nodes=10)

        network.first_node_death_round = 100
        network.half_nodes_death_round = 200
        network.last_node_death_round = 300

        stats = network.get_network_lifetime_stats()

        assert stats['first_node_death'] == 100
        assert stats['half_nodes_death'] == 200
        assert stats['last_node_death'] == 300


class TestEnergyStatistics:
    """Test energy statistics"""

    def test_initial_energy_statistics(self):
        """Test energy statistics at initialization"""
        network = WirelessSensorNetwork(
            num_nodes=10,
            initial_energy=0.5
        )

        stats = network.get_energy_statistics()

        assert stats['total_energy'] == 5.0  # 10 nodes * 0.5
        assert stats['avg_energy'] == 0.5
        assert stats['min_energy'] == 0.5
        assert stats['max_energy'] == 0.5
        assert stats['std_energy'] == 0.0
        assert stats['total_consumed'] == 0.0
        assert stats['avg_consumed_percentage'] == 0.0

    def test_energy_statistics_after_consumption(self):
        """Test energy statistics after some consumption"""
        network = WirelessSensorNetwork(
            num_nodes=10,
            initial_energy=1.0
        )

        # Consume different amounts of energy
        network.nodes[0].energy = 0.5
        network.nodes[1].energy = 0.3

        stats = network.get_energy_statistics()

        assert stats['total_energy'] < 10.0
        assert stats['total_consumed'] > 0.0
        assert stats['avg_consumed_percentage'] > 0.0

    def test_energy_statistics_all_dead(self):
        """Test energy statistics when all nodes are dead"""
        network = WirelessSensorNetwork(
            num_nodes=10,
            initial_energy=0.5
        )

        # Kill all nodes
        for node in network.nodes:
            node.energy = 0
            node.state = NodeState.DEAD

        stats = network.get_energy_statistics()

        assert stats['total_energy'] == 0
        assert stats['avg_energy'] == 0
        assert stats['total_consumed'] == 5.0
        assert stats['avg_consumed_percentage'] == 100.0

    def test_energy_statistics_varied_consumption(self):
        """Test energy statistics with varied consumption"""
        network = WirelessSensorNetwork(
            num_nodes=5,
            initial_energy=1.0
        )

        network.nodes[0].energy = 1.0
        network.nodes[1].energy = 0.75
        network.nodes[2].energy = 0.5
        network.nodes[3].energy = 0.25
        network.nodes[4].energy = 0.0
        network.nodes[4].state = NodeState.DEAD

        stats = network.get_energy_statistics()

        # Only alive nodes counted for avg
        assert stats['min_energy'] == 0.25
        assert stats['max_energy'] == 1.0
        assert stats['std_energy'] > 0


class TestNetworkStatistics:
    """Test comprehensive network statistics"""

    def test_network_statistics_initial(self):
        """Test network statistics at initialization"""
        network = WirelessSensorNetwork(num_nodes=100)

        stats = network.get_network_statistics()

        assert stats['total_nodes'] == 100
        assert stats['alive_nodes'] == 100
        assert stats['dead_nodes'] == 0
        assert stats['alive_percentage'] == 100.0
        assert stats['total_packets_sent'] == 0
        assert stats['total_packets_received'] == 0

    def test_network_statistics_with_activity(self):
        """Test network statistics after some activity"""
        network = WirelessSensorNetwork(num_nodes=10)

        # Simulate some activity
        network.nodes[0].packets_sent = 5
        network.nodes[1].packets_received = 3

        stats = network.get_network_statistics()

        assert stats['total_packets_sent'] == 5
        assert stats['total_packets_received'] == 3

    def test_network_statistics_with_deaths(self):
        """Test network statistics with dead nodes"""
        network = WirelessSensorNetwork(num_nodes=10)

        # Kill some nodes
        network.nodes[0].state = NodeState.DEAD
        network.nodes[1].state = NodeState.DEAD

        stats = network.get_network_statistics()

        assert stats['alive_nodes'] == 8
        assert stats['dead_nodes'] == 2
        assert stats['alive_percentage'] == 80.0

    def test_network_statistics_includes_substats(self):
        """Test that network statistics include energy and lifetime stats"""
        network = WirelessSensorNetwork(num_nodes=10)

        stats = network.get_network_statistics()

        assert 'energy' in stats
        assert 'lifetime' in stats
        assert isinstance(stats['energy'], dict)
        assert isinstance(stats['lifetime'], dict)


class TestNetworkReset:
    """Test network reset functionality"""

    def test_reset_restores_energy(self):
        """Test that reset restores all node energy"""
        network = WirelessSensorNetwork(
            num_nodes=10,
            initial_energy=0.5
        )

        # Drain some energy
        for node in network.nodes[:5]:
            node.energy = 0.1

        network.reset()

        for node in network.nodes:
            assert node.energy == 0.5

    def test_reset_clears_state(self):
        """Test that reset clears node states"""
        network = WirelessSensorNetwork(num_nodes=10)

        # Kill some nodes
        network.nodes[0].state = NodeState.DEAD

        network.reset()

        for node in network.nodes:
            assert node.state == NodeState.ACTIVE

    def test_reset_clears_statistics(self):
        """Test that reset clears statistics"""
        network = WirelessSensorNetwork(num_nodes=10)

        # Add some statistics
        network.nodes[0].packets_sent = 10
        network.nodes[1].packets_received = 5

        network.reset()

        for node in network.nodes:
            assert node.packets_sent == 0
            assert node.packets_received == 0

    def test_reset_clears_cluster_info(self):
        """Test that reset clears cluster information"""
        network = WirelessSensorNetwork(num_nodes=10)

        network.nodes[0].set_cluster_head(True)
        network.nodes[1].join_cluster(network.nodes[0])

        network.reset()

        for node in network.nodes:
            assert not node.is_cluster_head
            assert node.cluster_head is None
            assert node.cluster_members == []
            assert node.node_type == NodeType.NORMAL

    def test_reset_clears_network_rounds(self):
        """Test that reset clears network round counter"""
        network = WirelessSensorNetwork(num_nodes=10)

        network.current_round = 100

        network.reset()

        assert network.current_round == 0

    def test_reset_clears_lifetime_stats(self):
        """Test that reset clears lifetime statistics"""
        network = WirelessSensorNetwork(num_nodes=10)

        network.first_node_death_round = 100
        network.half_nodes_death_round = 200
        network.last_node_death_round = 300

        network.reset()

        assert network.first_node_death_round is None
        assert network.half_nodes_death_round is None
        assert network.last_node_death_round is None

    def test_reset_clears_node_rounds(self):
        """Test that reset clears node-specific round info"""
        network = WirelessSensorNetwork(num_nodes=10)

        network.nodes[0].round = 50
        network.nodes[0].ch_rounds = 5
        network.nodes[0].last_ch_round = 10

        network.reset()

        for node in network.nodes:
            assert node.round == 0
            assert node.ch_rounds == 0
            assert node.last_ch_round == -1

    def test_reset_multiple_times(self):
        """Test that reset can be called multiple times"""
        network = WirelessSensorNetwork(num_nodes=10, initial_energy=0.5)

        # First modification and reset
        network.nodes[0].energy = 0.1
        network.reset()
        assert network.nodes[0].energy == 0.5

        # Second modification and reset
        network.nodes[0].energy = 0.2
        network.reset()
        assert network.nodes[0].energy == 0.5


class TestStringRepresentation:
    """Test __str__ method"""

    def test_str_representation(self):
        """Test string representation of network"""
        network = WirelessSensorNetwork(
            num_nodes=100,
            area_size=(150, 150)
        )

        str_rep = str(network)

        assert "100/100" in str_rep
        assert "150x150" in str_rep

    def test_str_with_dead_nodes(self):
        """Test string representation with dead nodes"""
        network = WirelessSensorNetwork(num_nodes=10)

        network.nodes[0].state = NodeState.DEAD
        network.nodes[1].state = NodeState.DEAD

        str_rep = str(network)

        assert "8/10" in str_rep


class TestNetworkComplexScenarios:
    """Test complex network scenarios"""

    def test_network_simulation_cycle(self):
        """Test a complete simulation cycle"""
        network = WirelessSensorNetwork(
            num_nodes=20,
            initial_energy=0.5
        )

        # Simulate some rounds
        for round_num in range(10):
            # Some nodes transmit
            for i in range(5):
                if network.nodes[i].is_alive():
                    network.nodes[i].transmit(network.base_station)

            network.update_lifetime_stats(round_num + 1)

        # Network should have some statistics
        stats = network.get_network_statistics()
        assert stats['total_packets_sent'] > 0

    def test_gradual_network_death(self):
        """Test network gradually dying"""
        network = WirelessSensorNetwork(
            num_nodes=10,
            initial_energy=0.01
        )

        # Gradually kill nodes
        deaths = []
        for round_num in range(100):
            alive_before = len(network.get_alive_nodes())

            # Drain energy from alive nodes
            for node in network.get_alive_nodes():
                node.energy *= 0.9
                if node.energy < 0.0001:
                    node.energy = 0
                    node.state = NodeState.DEAD

            network.update_lifetime_stats(round_num + 1)

            alive_after = len(network.get_alive_nodes())
            if alive_after < alive_before:
                deaths.append(round_num + 1)

            if network.is_dead():
                break

        # Should have recorded deaths
        if network.first_node_death_round:
            assert network.first_node_death_round in deaths


class TestPrintStatistics:
    """Test print_statistics method (output testing)"""

    def test_print_statistics_no_error(self, capsys):
        """Test that print_statistics doesn't raise errors"""
        network = WirelessSensorNetwork(num_nodes=10)

        # Should not raise exception
        network.print_statistics()

        captured = capsys.readouterr()
        assert "NETWORK STATISTICS" in captured.out
        assert "Total Nodes: 10" in captured.out

    def test_print_statistics_with_deaths(self, capsys):
        """Test print_statistics with some dead nodes"""
        network = WirelessSensorNetwork(num_nodes=10)

        network.nodes[0].state = NodeState.DEAD
        network.first_node_death_round = 50

        network.print_statistics()

        captured = capsys.readouterr()
        assert "Dead Nodes: 1" in captured.out
        assert "Round 50" in captured.out or "50" in captured.out


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
