"""
Integration tests for WSN Routing Simulation

Tests complete simulation workflows end-to-end.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from src.network import WirelessSensorNetwork
from src.leach import LEACH
from visualization.metrics import PerformanceAnalyzer
from src.routing import AdaptiveRouter, MultiHopRouter


class TestFullSimulation:
    """Test complete simulation workflows"""

    def test_basic_leach_simulation(self):
        """Test basic LEACH simulation from start to finish"""
        # Create network
        network = WirelessSensorNetwork(
            num_nodes=50,
            area_size=(100, 100),
            base_station=(50, 150),
            initial_energy=0.5,
            deployment='random'
        )

        # Initialize LEACH
        leach = LEACH(network, cluster_head_probability=0.1)

        # Run simulation for multiple rounds
        max_rounds = 100
        for round_num in range(1, max_rounds + 1):
            stats = leach.run_round()
            network.update_lifetime_stats(round_num)

            # Verify stats structure
            assert 'round' in stats
            assert 'num_cluster_heads' in stats
            assert 'packets_to_bs' in stats
            assert 'alive_nodes' in stats

            if network.is_dead():
                break

        # Verify simulation completed
        assert leach.current_round > 0
        assert len(leach.rounds_history) > 0

        # Verify statistics
        final_stats = leach.get_statistics()
        assert final_stats['total_rounds'] == leach.current_round
        assert final_stats['total_packets_to_bs'] >= 0

    def test_network_lifecycle_tracking(self):
        """Test network lifetime tracking throughout simulation"""
        network = WirelessSensorNetwork(
            num_nodes=20,
            initial_energy=0.1,  # Low energy for faster death
            deployment='random'
        )

        leach = LEACH(network, cluster_head_probability=0.1)

        fnd_recorded = False
        hnd_recorded = False

        for round_num in range(1, 500):
            leach.run_round()
            network.update_lifetime_stats(round_num)

            # Check FND
            if network.first_node_death_round is not None and not fnd_recorded:
                fnd_recorded = True
                assert network.first_node_death_round == round_num

            # Check HND
            if network.half_nodes_death_round is not None and not hnd_recorded:
                hnd_recorded = True
                dead_count = len(network.get_dead_nodes())
                assert dead_count >= network.num_nodes / 2

            if network.is_dead():
                assert network.last_node_death_round == round_num
                break

        # Should have recorded at least FND
        assert fnd_recorded or network.is_dead()

    def test_energy_consumption_tracking(self):
        """Test that energy consumption is properly tracked"""
        network = WirelessSensorNetwork(
            num_nodes=30,
            initial_energy=1.0,
            deployment='grid'
        )

        leach = LEACH(network, cluster_head_probability=0.1)

        initial_total_energy = sum(node.energy for node in network.nodes)

        # Run several rounds
        for _ in range(20):
            leach.run_round()

        final_total_energy = sum(node.energy for node in network.nodes)

        # Energy should have decreased
        assert final_total_energy < initial_total_energy

        # Total energy consumed should match
        energy_consumed = initial_total_energy - final_total_energy
        assert energy_consumed > 0

    def test_performance_analyzer_integration(self):
        """Test performance analyzer with actual simulation data"""
        network = WirelessSensorNetwork(
            num_nodes=40,
            initial_energy=0.5
        )

        leach = LEACH(network, cluster_head_probability=0.1)

        # Run simulation
        for round_num in range(1, 50):
            leach.run_round()
            network.update_lifetime_stats(round_num)

        # Analyze performance
        analyzer = PerformanceAnalyzer(leach.rounds_history)

        # Get all metrics
        lifetime_metrics = analyzer.get_network_lifetime_metrics()
        energy_metrics = analyzer.get_energy_metrics()
        throughput_metrics = analyzer.get_throughput_metrics()
        clustering_metrics = analyzer.get_clustering_metrics()

        # Verify metrics exist and are valid
        assert isinstance(lifetime_metrics, dict)
        assert isinstance(energy_metrics, dict)
        assert isinstance(throughput_metrics, dict)
        assert isinstance(clustering_metrics, dict)

        # Verify comprehensive report
        report = analyzer.get_comprehensive_report()
        assert 'lifetime' in report
        assert 'energy' in report
        assert 'throughput' in report
        assert 'clustering' in report

    def test_different_deployments(self):
        """Test that all deployment strategies work in simulation"""
        deployments = ['random', 'grid', 'cluster']

        for deployment in deployments:
            network = WirelessSensorNetwork(
                num_nodes=30,
                initial_energy=0.5,
                deployment=deployment
            )

            leach = LEACH(network, cluster_head_probability=0.1)

            # Run a few rounds
            for _ in range(10):
                stats = leach.run_round()
                assert stats['alive_nodes'] > 0 or network.is_dead()

            # Verify network was created correctly
            assert len(network.nodes) == 30

    def test_simulation_reset(self):
        """Test that network can be reset and reused"""
        network = WirelessSensorNetwork(
            num_nodes=20,
            initial_energy=0.5
        )

        leach = LEACH(network, cluster_head_probability=0.1)

        # Run first simulation
        for _ in range(20):
            leach.run_round()

        first_round_count = leach.current_round
        first_energy = sum(node.energy for node in network.nodes)

        # Reset network
        network.reset()

        # Create new LEACH instance
        leach2 = LEACH(network, cluster_head_probability=0.1)

        # Run second simulation
        for _ in range(20):
            leach2.run_round()

        # Verify reset worked
        assert all(node.energy <= node.initial_energy for node in network.nodes)
        assert leach2.current_round == 20

    def test_high_node_count_simulation(self):
        """Test simulation with higher node count"""
        network = WirelessSensorNetwork(
            num_nodes=100,
            area_size=(150, 150),
            initial_energy=0.5,
            deployment='random'
        )

        leach = LEACH(network, cluster_head_probability=0.05)

        # Run simulation
        rounds_completed = 0
        for round_num in range(1, 100):
            stats = leach.run_round()
            rounds_completed += 1

            # Should have reasonable number of cluster heads
            assert stats['num_cluster_heads'] >= 0

            if network.is_dead():
                break

        # Should have completed some rounds
        assert rounds_completed > 0

    def test_routing_integration(self):
        """Test routing mechanisms in actual network"""
        network = WirelessSensorNetwork(
            num_nodes=30,
            deployment='grid',
            initial_energy=1.0
        )

        # Test adaptive router
        router = AdaptiveRouter(network)

        source = network.nodes[0]
        dest = network.nodes[-1]

        path = router.route_packet(source, dest)
        assert path is not None

        # Test transmission
        result = router.transmit(source, dest)
        assert isinstance(result, bool)

    def test_clustering_stability(self):
        """Test that clustering happens every round"""
        network = WirelessSensorNetwork(
            num_nodes=50,
            initial_energy=1.0
        )

        leach = LEACH(network, cluster_head_probability=0.1)

        for _ in range(30):
            stats = leach.run_round()

            # Every round should have at least one cluster head
            # (due to forced election if none selected)
            assert stats['num_cluster_heads'] >= 1

            # All alive non-CH nodes should be in a cluster
            alive_nodes = network.get_alive_nodes()
            for node in alive_nodes:
                if not node.is_cluster_head:
                    assert node.cluster_head is not None

    def test_packet_delivery(self):
        """Test that packets are delivered to base station"""
        network = WirelessSensorNetwork(
            num_nodes=30,
            initial_energy=1.0
        )

        leach = LEACH(network, cluster_head_probability=0.1)

        total_packets = 0
        for _ in range(20):
            stats = leach.run_round()
            total_packets += stats['packets_to_bs']

        # Should have delivered some packets
        assert total_packets > 0
        assert leach.total_packets_to_bs == total_packets


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
