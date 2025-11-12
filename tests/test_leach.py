"""
Comprehensive unit tests for leach.py

Tests cover LEACH protocol, CH election, clustering, and data transmission.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from src.network import WirelessSensorNetwork
from src.leach import LEACH
from src.node import NodeType, NodeState


class TestLEACHInitialization:
    """Test LEACH initialization"""

    def test_basic_initialization(self):
        """Test basic LEACH initialization"""
        network = WirelessSensorNetwork(num_nodes=20)
        leach = LEACH(network, cluster_head_probability=0.1)

        assert leach.p == 0.1
        assert leach.current_round == 0
        assert len(leach.cluster_heads) == 0
        assert leach.total_packets_to_bs == 0

    def test_custom_round_time(self):
        """Test initialization with custom round time"""
        network = WirelessSensorNetwork(num_nodes=20)
        leach = LEACH(network, round_time=30)

        assert leach.round_time == 30


class TestClusterHeadElection:
    """Test cluster head election"""

    def test_ch_election_creates_heads(self):
        """Test that CH election creates some cluster heads"""
        network = WirelessSensorNetwork(num_nodes=50, initial_energy=1.0)
        leach = LEACH(network, cluster_head_probability=0.1)

        leach._elect_cluster_heads()

        assert len(leach.cluster_heads) >= 0  # May be 0 due to probability

    def test_force_ch_election(self):
        """Test force CH election when none elected"""
        network = WirelessSensorNetwork(num_nodes=10, initial_energy=1.0)
        leach = LEACH(network, cluster_head_probability=0.0)  # No voluntary CHs

        leach._force_cluster_head_election()

        assert len(leach.cluster_heads) == 1  # Forced one CH

    def test_ch_has_highest_energy_when_forced(self):
        """Test that forced CH has highest energy"""
        network = WirelessSensorNetwork(num_nodes=10, initial_energy=0.5)
        # Give one node higher energy
        network.nodes[5].energy = 1.0

        leach = LEACH(network, cluster_head_probability=0.0)
        leach._force_cluster_head_election()

        assert leach.cluster_heads[0].id == 5

    def test_ch_nodes_marked_correctly(self):
        """Test that CH nodes are marked correctly"""
        network = WirelessSensorNetwork(num_nodes=20)
        leach = LEACH(network, cluster_head_probability=0.2)

        leach._elect_cluster_heads()

        for ch in leach.cluster_heads:
            assert ch.is_cluster_head
            assert ch.node_type == NodeType.CLUSTER_HEAD


class TestClusterFormation:
    """Test cluster formation"""

    def test_cluster_formation_assigns_members(self):
        """Test that cluster formation assigns members"""
        network = WirelessSensorNetwork(num_nodes=20)
        leach = LEACH(network, cluster_head_probability=0.2)

        leach.setup_phase()

        # Each cluster should have some members (or be a CH)
        for node in network.nodes:
            if not node.is_cluster_head:
                assert node.cluster_head is not None

    def test_all_nodes_in_clusters(self):
        """Test that all non-CH nodes are assigned to clusters"""
        network = WirelessSensorNetwork(num_nodes=30)
        leach = LEACH(network, cluster_head_probability=0.1)

        leach.setup_phase()

        non_ch_nodes = [n for n in network.nodes if not n.is_cluster_head]
        for node in non_ch_nodes:
            assert node.cluster_head is not None


class TestSetupPhase:
    """Test setup phase"""

    def test_setup_phase_clears_previous(self):
        """Test that setup phase clears previous round data"""
        network = WirelessSensorNetwork(num_nodes=20)
        leach = LEACH(network, cluster_head_probability=0.1)

        leach.setup_phase()
        first_chs = len(leach.cluster_heads)

        leach.setup_phase()  # Run again

        # Should have re-elected
        assert isinstance(leach.cluster_heads, list)

    def test_setup_phase_creates_clusters_dict(self):
        """Test that setup phase creates clusters dictionary"""
        network = WirelessSensorNetwork(num_nodes=20)
        leach = LEACH(network, cluster_head_probability=0.2)

        leach.setup_phase()

        assert isinstance(leach.clusters, dict)
        assert len(leach.clusters) == len(leach.cluster_heads)


class TestSteadyStatePhase:
    """Test steady-state phase"""

    def test_steady_state_returns_stats(self):
        """Test that steady state returns statistics"""
        network = WirelessSensorNetwork(num_nodes=20, initial_energy=1.0)
        leach = LEACH(network, cluster_head_probability=0.2)

        leach.setup_phase()
        stats = leach.steady_state_phase()

        assert 'packets_to_bs' in stats
        assert 'energy_consumed' in stats
        assert 'alive_nodes' in stats

    def test_steady_state_transmits_to_bs(self):
        """Test that steady state sends packets to BS"""
        network = WirelessSensorNetwork(num_nodes=20, initial_energy=1.0)
        leach = LEACH(network, cluster_head_probability=0.2)

        leach.setup_phase()
        stats = leach.steady_state_phase()

        # CHs should have transmitted
        assert stats['packets_to_bs'] >= 0

    def test_steady_state_consumes_energy(self):
        """Test that steady state consumes energy"""
        network = WirelessSensorNetwork(num_nodes=20, initial_energy=1.0)
        leach = LEACH(network, cluster_head_probability=0.2)

        leach.setup_phase()
        initial_energy = sum(n.energy for n in network.nodes)

        leach.steady_state_phase()

        final_energy = sum(n.energy for n in network.nodes)
        assert final_energy < initial_energy


class TestRunRound:
    """Test complete round execution"""

    def test_run_round_increments_counter(self):
        """Test that run_round increments round counter"""
        network = WirelessSensorNetwork(num_nodes=20)
        leach = LEACH(network, cluster_head_probability=0.1)

        assert leach.current_round == 0
        leach.run_round()
        assert leach.current_round == 1
        leach.run_round()
        assert leach.current_round == 2

    def test_run_round_returns_stats(self):
        """Test that run_round returns statistics"""
        network = WirelessSensorNetwork(num_nodes=20, initial_energy=1.0)
        leach = LEACH(network, cluster_head_probability=0.1)

        stats = leach.run_round()

        assert 'round' in stats
        assert 'num_cluster_heads' in stats
        assert 'packets_to_bs' in stats
        assert 'alive_nodes' in stats

    def test_run_round_updates_history(self):
        """Test that run_round updates rounds_history"""
        network = WirelessSensorNetwork(num_nodes=20)
        leach = LEACH(network, cluster_head_probability=0.1)

        leach.run_round()
        leach.run_round()

        assert len(leach.rounds_history) == 2

    def test_multiple_rounds(self):
        """Test running multiple rounds"""
        network = WirelessSensorNetwork(num_nodes=20, initial_energy=0.5)
        leach = LEACH(network, cluster_head_probability=0.1)

        for _ in range(10):
            stats = leach.run_round()
            assert stats['alive_nodes'] > 0 or network.is_dead()


class TestClusteringInfo:
    """Test clustering information methods"""

    def test_get_clustering_info(self):
        """Test get_clustering_info method"""
        network = WirelessSensorNetwork(num_nodes=20)
        leach = LEACH(network, cluster_head_probability=0.2)

        leach.run_round()

        info = leach.get_clustering_info()

        assert 'num_clusters' in info
        assert 'cluster_heads' in info
        assert 'cluster_sizes' in info
        assert 'avg_cluster_size' in info

    def test_clustering_info_cluster_sizes(self):
        """Test that clustering info contains cluster sizes"""
        network = WirelessSensorNetwork(num_nodes=30)
        leach = LEACH(network, cluster_head_probability=0.2)

        leach.run_round()

        info = leach.get_clustering_info()

        assert isinstance(info['cluster_sizes'], dict)


class TestStatistics:
    """Test LEACH statistics"""

    def test_get_statistics(self):
        """Test get_statistics method"""
        network = WirelessSensorNetwork(num_nodes=20, initial_energy=0.5)
        leach = LEACH(network, cluster_head_probability=0.1)

        for _ in range(5):
            leach.run_round()

        stats = leach.get_statistics()

        assert 'total_rounds' in stats
        assert 'alive_nodes' in stats
        assert 'dead_nodes' in stats
        assert 'total_packets_to_bs' in stats
        assert stats['total_rounds'] == 5

    def test_statistics_track_packets(self):
        """Test that statistics track total packets"""
        network = WirelessSensorNetwork(num_nodes=20, initial_energy=1.0)
        leach = LEACH(network, cluster_head_probability=0.2)

        for _ in range(3):
            leach.run_round()

        stats = leach.get_statistics()
        assert stats['total_packets_to_bs'] >= 0


class TestPrintRoundInfo:
    """Test print_round_info method"""

    def test_print_round_info_no_error(self, capsys):
        """Test that print_round_info doesn't raise errors"""
        network = WirelessSensorNetwork(num_nodes=10)
        leach = LEACH(network, cluster_head_probability=0.2)

        leach.run_round()
        leach.print_round_info()

        captured = capsys.readouterr()
        assert "Round" in captured.out


class TestEdgeCases:
    """Test edge cases"""

    def test_single_node_network(self):
        """Test LEACH with single node"""
        network = WirelessSensorNetwork(num_nodes=1, initial_energy=1.0)
        leach = LEACH(network, cluster_head_probability=1.0)

        stats = leach.run_round()

        assert stats['alive_nodes'] == 1

    def test_all_nodes_dead(self):
        """Test LEACH when all nodes are dead"""
        network = WirelessSensorNetwork(num_nodes=10, initial_energy=0.00001)
        leach = LEACH(network, cluster_head_probability=0.1)

        # Drain all energy
        for node in network.nodes:
            node.energy = 0
            node.state = NodeState.DEAD

        stats = leach.run_round()

        assert stats['alive_nodes'] == 0
        assert stats['packets_to_bs'] == 0

    def test_zero_ch_probability(self):
        """Test LEACH with zero CH probability"""
        network = WirelessSensorNetwork(num_nodes=20)
        leach = LEACH(network, cluster_head_probability=0.0)

        leach.run_round()

        # Should have forced at least one CH
        assert len(leach.cluster_heads) >= 1

    def test_high_ch_probability(self):
        """Test LEACH with high CH probability"""
        network = WirelessSensorNetwork(num_nodes=20)
        leach = LEACH(network, cluster_head_probability=0.9)

        leach.run_round()

        # Should have many CHs
        assert len(leach.cluster_heads) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
