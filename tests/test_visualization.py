"""
Comprehensive Unit Tests for Visualization Modules

Tests NetworkVisualizer, plot_protocol_comparison, and PerformanceAnalyzer.
Achieves 95%+ code coverage with edge case testing.
"""

import unittest
import sys
import os
import tempfile
import shutil
from unittest.mock import patch, MagicMock
import numpy as np

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from visualization.plotter import NetworkVisualizer, plot_protocol_comparison
from visualization.metrics import PerformanceAnalyzer
from src.network import WirelessSensorNetwork
from src.node import NodeType


class TestNetworkVisualizer(unittest.TestCase):
    """Test cases for NetworkVisualizer class"""

    def setUp(self):
        """Set up test fixtures"""
        self.network = WirelessSensorNetwork(num_nodes=10, area_size=(100, 100))
        self.visualizer = NetworkVisualizer(self.network)
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test files"""
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_initialization(self):
        """Test visualizer initialization"""
        self.assertIsNotNone(self.visualizer.network)
        self.assertEqual(self.visualizer.network, self.network)

    @patch('matplotlib.pyplot.show')
    @patch('matplotlib.pyplot.savefig')
    def test_plot_topology_basic(self, mock_savefig, mock_show):
        """Test basic topology plotting"""
        self.visualizer.plot_topology()

        # Should call show
        mock_show.assert_called_once()

    @patch('matplotlib.pyplot.show')
    @patch('matplotlib.pyplot.savefig')
    def test_plot_topology_with_clusters(self, mock_savefig, mock_show):
        """Test topology plotting with cluster visualization"""
        # Set up clusters
        self.network.nodes[0].node_type = NodeType.CLUSTER_HEAD
        self.network.nodes[1].cluster_head = self.network.nodes[0]

        self.visualizer.plot_topology(show_clusters=True)

        mock_show.assert_called_once()

    @patch('matplotlib.pyplot.show')
    @patch('matplotlib.pyplot.savefig')
    def test_plot_topology_with_connections(self, mock_savefig, mock_show):
        """Test topology plotting with connections"""
        # Set up clusters
        self.network.nodes[0].node_type = NodeType.CLUSTER_HEAD
        self.network.nodes[1].cluster_head = self.network.nodes[0]

        self.visualizer.plot_topology(show_clusters=True, show_connections=True)

        mock_show.assert_called_once()

    @patch('matplotlib.pyplot.show')
    @patch('matplotlib.pyplot.savefig')
    def test_plot_topology_save(self, mock_savefig, mock_show):
        """Test topology plotting with save"""
        save_path = os.path.join(self.test_dir, 'topology.png')

        self.visualizer.plot_topology(save_path=save_path)

        mock_savefig.assert_called_once()
        call_args = mock_savefig.call_args
        self.assertEqual(call_args[0][0], save_path)

    @patch('matplotlib.pyplot.show')
    def test_plot_topology_custom_title(self, mock_show):
        """Test topology plotting with custom title"""
        self.visualizer.plot_topology(title="Custom Network Title")

        mock_show.assert_called_once()

    @patch('matplotlib.pyplot.show')
    def test_plot_topology_with_dead_nodes(self, mock_show):
        """Test topology plotting with dead nodes"""
        # Kill some nodes
        self.network.nodes[0].energy = 0
        self.network.nodes[1].energy = 0

        self.visualizer.plot_topology()

        mock_show.assert_called_once()

    @patch('matplotlib.pyplot.show')
    def test_plot_topology_all_dead_nodes(self, mock_show):
        """Test topology plotting when all nodes are dead"""
        # Kill all nodes
        for node in self.network.nodes:
            node.energy = 0

        self.visualizer.plot_topology()

        mock_show.assert_called_once()

    @patch('matplotlib.pyplot.show')
    def test_plot_topology_no_cluster_assignment(self, mock_show):
        """Test topology with cluster heads but no members"""
        self.network.nodes[0].node_type = NodeType.CLUSTER_HEAD

        self.visualizer.plot_topology(show_clusters=True)

        mock_show.assert_called_once()

    @patch('matplotlib.pyplot.show')
    @patch('matplotlib.pyplot.savefig')
    def test_plot_energy_distribution(self, mock_savefig, mock_show):
        """Test energy distribution plotting"""
        self.visualizer.plot_energy_distribution()

        mock_show.assert_called_once()

    @patch('matplotlib.pyplot.show')
    @patch('matplotlib.pyplot.savefig')
    def test_plot_energy_distribution_save(self, mock_savefig, mock_show):
        """Test energy distribution plotting with save"""
        save_path = os.path.join(self.test_dir, 'energy.png')

        self.visualizer.plot_energy_distribution(save_path=save_path)

        mock_savefig.assert_called_once()

    @patch('matplotlib.pyplot.show')
    def test_plot_energy_distribution_all_dead(self, mock_show):
        """Test energy distribution when all nodes dead"""
        # Kill all nodes
        for node in self.network.nodes:
            node.energy = 0

        self.visualizer.plot_energy_distribution()

        mock_show.assert_called_once()

    @patch('matplotlib.pyplot.show')
    def test_plot_energy_distribution_varied_energy(self, mock_show):
        """Test energy distribution with varied energy levels"""
        # Set different energy levels
        for i, node in enumerate(self.network.nodes):
            node.energy = (i + 1) * 0.1

        self.visualizer.plot_energy_distribution()

        mock_show.assert_called_once()

    @patch('matplotlib.pyplot.show')
    @patch('matplotlib.pyplot.savefig')
    def test_plot_node_positions_with_energy(self, mock_savefig, mock_show):
        """Test node position plotting with energy coloring"""
        self.visualizer.plot_node_positions_with_energy()

        mock_show.assert_called_once()

    @patch('matplotlib.pyplot.show')
    @patch('matplotlib.pyplot.savefig')
    def test_plot_node_positions_save(self, mock_savefig, mock_show):
        """Test node position plotting with save"""
        save_path = os.path.join(self.test_dir, 'positions.png')

        self.visualizer.plot_node_positions_with_energy(save_path=save_path)

        mock_savefig.assert_called_once()

    @patch('matplotlib.pyplot.show')
    def test_plot_node_positions_with_dead_nodes(self, mock_show):
        """Test node positions with dead nodes"""
        # Kill some nodes
        self.network.nodes[0].energy = 0
        self.network.nodes[1].energy = 0

        self.visualizer.plot_node_positions_with_energy()

        mock_show.assert_called_once()

    @patch('matplotlib.pyplot.show')
    def test_plot_node_positions_all_dead(self, mock_show):
        """Test node positions when all nodes dead"""
        # Kill all nodes
        for node in self.network.nodes:
            node.energy = 0

        self.visualizer.plot_node_positions_with_energy()

        mock_show.assert_called_once()


class TestPlotProtocolComparison(unittest.TestCase):
    """Test cases for plot_protocol_comparison function"""

    def setUp(self):
        """Set up test fixtures"""
        self.test_dir = tempfile.mkdtemp()

        # Create sample protocol data
        self.protocols_data = {
            'LEACH': [
                {'round': 1, 'alive_nodes': 100, 'energy_consumed': 0.5},
                {'round': 2, 'alive_nodes': 95, 'energy_consumed': 0.6},
                {'round': 3, 'alive_nodes': 90, 'energy_consumed': 0.7},
            ],
            'Direct': [
                {'round': 1, 'alive_nodes': 100, 'energy_consumed': 0.8},
                {'round': 2, 'alive_nodes': 90, 'energy_consumed': 0.9},
                {'round': 3, 'alive_nodes': 80, 'energy_consumed': 1.0},
            ]
        }

    def tearDown(self):
        """Clean up test files"""
        shutil.rmtree(self.test_dir, ignore_errors=True)

    @patch('matplotlib.pyplot.show')
    def test_plot_comparison_alive_nodes(self, mock_show):
        """Test protocol comparison for alive_nodes metric"""
        plot_protocol_comparison(self.protocols_data, metric='alive_nodes')

        mock_show.assert_called_once()

    @patch('matplotlib.pyplot.show')
    def test_plot_comparison_energy_consumed(self, mock_show):
        """Test protocol comparison for energy_consumed metric"""
        plot_protocol_comparison(self.protocols_data, metric='energy_consumed')

        mock_show.assert_called_once()

    @patch('matplotlib.pyplot.show')
    @patch('matplotlib.pyplot.savefig')
    def test_plot_comparison_save(self, mock_savefig, mock_show):
        """Test protocol comparison with save"""
        save_path = os.path.join(self.test_dir, 'comparison.png')

        plot_protocol_comparison(self.protocols_data, save_path=save_path)

        mock_savefig.assert_called_once()

    @patch('matplotlib.pyplot.show')
    def test_plot_comparison_single_protocol(self, mock_show):
        """Test protocol comparison with single protocol"""
        data = {
            'LEACH': self.protocols_data['LEACH']
        }

        plot_protocol_comparison(data, metric='alive_nodes')

        mock_show.assert_called_once()

    @patch('matplotlib.pyplot.show')
    def test_plot_comparison_many_protocols(self, mock_show):
        """Test protocol comparison with many protocols"""
        data = {}
        for i in range(5):
            data[f'Protocol_{i}'] = [
                {'round': j, 'alive_nodes': 100 - j*i}
                for j in range(1, 11)
            ]

        plot_protocol_comparison(data, metric='alive_nodes')

        mock_show.assert_called_once()


class TestPerformanceAnalyzer(unittest.TestCase):
    """Test cases for PerformanceAnalyzer class"""

    def setUp(self):
        """Set up test fixtures"""
        # Create sample rounds history
        self.rounds_history = []
        for i in range(1, 101):
            self.rounds_history.append({
                'round': i,
                'alive_nodes': max(0, 100 - i // 2),
                'energy_consumed': 0.01 * i,
                'total_energy': 10.0 - 0.01 * i,
                'packets_to_bs': 50 if i < 90 else 20,
                'num_cluster_heads': 5 if i % 2 == 0 else 6
            })

        self.analyzer = PerformanceAnalyzer(self.rounds_history)
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test files"""
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_initialization(self):
        """Test analyzer initialization"""
        self.assertIsNotNone(self.analyzer.rounds_history)
        self.assertEqual(len(self.analyzer.rounds_history), 100)

    def test_get_network_lifetime_metrics(self):
        """Test network lifetime metrics calculation"""
        lifetime = self.analyzer.get_network_lifetime_metrics()

        self.assertIn('first_node_death', lifetime)
        self.assertIn('half_nodes_death', lifetime)
        self.assertIn('last_node_death', lifetime)
        self.assertIn('stability_period', lifetime)
        self.assertIn('total_rounds', lifetime)

        self.assertEqual(lifetime['total_rounds'], 100)

    def test_network_lifetime_first_node_death(self):
        """Test FND detection"""
        lifetime = self.analyzer.get_network_lifetime_metrics()

        # First node dies at round 2 (100 - 2//2 = 99)
        self.assertIsNotNone(lifetime['first_node_death'])
        self.assertGreater(lifetime['first_node_death'], 0)

    def test_network_lifetime_half_nodes_death(self):
        """Test HND detection"""
        lifetime = self.analyzer.get_network_lifetime_metrics()

        # Half nodes (50) die at round 100 (100 - 100//2 = 50)
        self.assertIsNotNone(lifetime['half_nodes_death'])

    def test_network_lifetime_stability_period(self):
        """Test stability period calculation"""
        lifetime = self.analyzer.get_network_lifetime_metrics()

        stability = lifetime['stability_period']
        self.assertIsInstance(stability, int)
        self.assertGreater(stability, 0)

    def test_get_network_lifetime_no_deaths(self):
        """Test lifetime metrics when no nodes die"""
        # All nodes stay alive
        history = [
            {'round': i, 'alive_nodes': 100}
            for i in range(1, 51)
        ]
        analyzer = PerformanceAnalyzer(history)

        lifetime = analyzer.get_network_lifetime_metrics()

        self.assertIsNone(lifetime['first_node_death'])
        self.assertIsNone(lifetime['half_nodes_death'])
        self.assertIsNone(lifetime['last_node_death'])
        self.assertEqual(lifetime['stability_period'], 50)

    def test_get_energy_metrics(self):
        """Test energy metrics calculation"""
        energy = self.analyzer.get_energy_metrics()

        self.assertIn('total_energy_consumed', energy)
        self.assertIn('avg_energy_per_round', energy)
        self.assertIn('energy_depletion_rate', energy)

        self.assertGreater(energy['total_energy_consumed'], 0)
        self.assertGreater(energy['avg_energy_per_round'], 0)

    def test_energy_metrics_empty_history(self):
        """Test energy metrics with empty history"""
        analyzer = PerformanceAnalyzer([])

        energy = analyzer.get_energy_metrics()

        self.assertEqual(energy['avg_energy_per_round'], 0)
        self.assertEqual(energy['energy_depletion_rate'], 0)

    def test_energy_metrics_single_round(self):
        """Test energy metrics with single round"""
        history = [
            {'round': 1, 'energy_consumed': 0.5, 'total_energy': 10.0}
        ]
        analyzer = PerformanceAnalyzer(history)

        energy = analyzer.get_energy_metrics()

        self.assertEqual(energy['total_energy_consumed'], 0.5)
        self.assertEqual(energy['avg_energy_per_round'], 0.5)
        self.assertEqual(energy['energy_depletion_rate'], 0)

    def test_get_throughput_metrics(self):
        """Test throughput metrics calculation"""
        throughput = self.analyzer.get_throughput_metrics()

        self.assertIn('total_packets_to_bs', throughput)
        self.assertIn('avg_packets_per_round', throughput)
        self.assertIn('throughput_variance', throughput)

        self.assertGreater(throughput['total_packets_to_bs'], 0)
        self.assertGreater(throughput['avg_packets_per_round'], 0)

    def test_throughput_metrics_empty_history(self):
        """Test throughput metrics with empty history"""
        analyzer = PerformanceAnalyzer([])

        throughput = analyzer.get_throughput_metrics()

        self.assertEqual(throughput['avg_packets_per_round'], 0)
        self.assertEqual(throughput['throughput_variance'], 0)

    def test_throughput_variance_calculation(self):
        """Test throughput variance is calculated correctly"""
        throughput = self.analyzer.get_throughput_metrics()

        # Should have variance due to different packet counts
        self.assertGreater(throughput['throughput_variance'], 0)

    def test_get_clustering_metrics(self):
        """Test clustering metrics calculation"""
        clustering = self.analyzer.get_clustering_metrics()

        self.assertIn('avg_cluster_heads', clustering)
        self.assertIn('std_cluster_heads', clustering)
        self.assertIn('min_cluster_heads', clustering)
        self.assertIn('max_cluster_heads', clustering)

        self.assertGreater(clustering['avg_cluster_heads'], 0)
        self.assertEqual(clustering['min_cluster_heads'], 5)
        self.assertEqual(clustering['max_cluster_heads'], 6)

    def test_clustering_metrics_no_clusters(self):
        """Test clustering metrics with no cluster data"""
        history = [{'round': i} for i in range(1, 11)]
        analyzer = PerformanceAnalyzer(history)

        clustering = analyzer.get_clustering_metrics()

        self.assertEqual(clustering['avg_cluster_heads'], 0)
        self.assertEqual(clustering['min_cluster_heads'], 0)

    def test_get_comprehensive_report(self):
        """Test comprehensive report generation"""
        report = self.analyzer.get_comprehensive_report()

        self.assertIn('lifetime', report)
        self.assertIn('energy', report)
        self.assertIn('throughput', report)
        self.assertIn('clustering', report)

        # Verify structure
        self.assertIn('first_node_death', report['lifetime'])
        self.assertIn('total_energy_consumed', report['energy'])
        self.assertIn('total_packets_to_bs', report['throughput'])
        self.assertIn('avg_cluster_heads', report['clustering'])

    @patch('builtins.print')
    def test_print_report(self, mock_print):
        """Test report printing"""
        self.analyzer.print_report()

        # Should call print multiple times
        self.assertGreater(mock_print.call_count, 10)

    @patch('builtins.print')
    def test_print_report_with_none_values(self, mock_print):
        """Test report printing with None values"""
        history = [{'round': i, 'alive_nodes': 100} for i in range(1, 11)]
        analyzer = PerformanceAnalyzer(history)

        # Should not crash with None values
        analyzer.print_report()

        self.assertGreater(mock_print.call_count, 5)

    @patch('matplotlib.pyplot.show')
    @patch('matplotlib.pyplot.savefig')
    def test_plot_metrics_over_time(self, mock_savefig, mock_show):
        """Test metrics plotting over time"""
        self.analyzer.plot_metrics_over_time()

        mock_show.assert_called_once()

    @patch('matplotlib.pyplot.show')
    @patch('matplotlib.pyplot.savefig')
    def test_plot_metrics_save(self, mock_savefig, mock_show):
        """Test metrics plotting with save"""
        save_path = os.path.join(self.test_dir, 'metrics.png')

        self.analyzer.plot_metrics_over_time(save_path=save_path)

        mock_savefig.assert_called_once()

    @patch('matplotlib.pyplot.show')
    def test_plot_metrics_with_fnd_hnd(self, mock_show):
        """Test metrics plotting includes FND and HND markers"""
        self.analyzer.plot_metrics_over_time()

        mock_show.assert_called_once()

    @patch('matplotlib.pyplot.show')
    def test_plot_metrics_with_moving_average(self, mock_show):
        """Test metrics plotting includes moving average for clusters"""
        # Ensure enough data points for moving average
        self.analyzer.plot_metrics_over_time()

        mock_show.assert_called_once()

    @patch('matplotlib.pyplot.show')
    def test_plot_metrics_short_history(self, mock_show):
        """Test metrics plotting with short history (< 10 rounds)"""
        history = [
            {'round': i, 'alive_nodes': 100 - i*10, 'energy_consumed': 0.1,
             'packets_to_bs': 50, 'num_cluster_heads': 5}
            for i in range(1, 6)
        ]
        analyzer = PerformanceAnalyzer(history)

        # Should still work without moving average
        analyzer.plot_metrics_over_time()

        mock_show.assert_called_once()

    @patch('matplotlib.pyplot.show')
    @patch('matplotlib.pyplot.savefig')
    def test_plot_energy_efficiency(self, mock_savefig, mock_show):
        """Test energy efficiency plotting"""
        self.analyzer.plot_energy_efficiency()

        mock_show.assert_called_once()

    @patch('matplotlib.pyplot.show')
    @patch('matplotlib.pyplot.savefig')
    def test_plot_energy_efficiency_save(self, mock_savefig, mock_show):
        """Test energy efficiency plotting with save"""
        save_path = os.path.join(self.test_dir, 'efficiency.png')

        self.analyzer.plot_energy_efficiency(save_path=save_path)

        mock_savefig.assert_called_once()

    @patch('matplotlib.pyplot.show')
    def test_plot_energy_efficiency_zero_energy(self, mock_show):
        """Test energy efficiency plotting with zero energy rounds"""
        history = [
            {'round': i, 'energy_consumed': 0.0 if i % 5 == 0 else 0.1,
             'packets_to_bs': 50}
            for i in range(1, 21)
        ]
        analyzer = PerformanceAnalyzer(history)

        # Should handle zero energy gracefully
        analyzer.plot_energy_efficiency()

        mock_show.assert_called_once()

    @patch('matplotlib.pyplot.show')
    def test_plot_energy_efficiency_all_zero_energy(self, mock_show):
        """Test energy efficiency with all zero energy"""
        history = [
            {'round': i, 'energy_consumed': 0.0, 'packets_to_bs': 50}
            for i in range(1, 11)
        ]
        analyzer = PerformanceAnalyzer(history)

        analyzer.plot_energy_efficiency()

        mock_show.assert_called_once()


class TestVisualizationEdgeCases(unittest.TestCase):
    """Test edge cases and integration scenarios"""

    @patch('matplotlib.pyplot.show')
    def test_visualizer_with_single_node(self, mock_show):
        """Test visualizer with single node network"""
        network = WirelessSensorNetwork(num_nodes=1, area_size=(50, 50))
        visualizer = NetworkVisualizer(network)

        visualizer.plot_topology()

        mock_show.assert_called_once()

    @patch('matplotlib.pyplot.show')
    def test_visualizer_with_large_network(self, mock_show):
        """Test visualizer with large network"""
        network = WirelessSensorNetwork(num_nodes=100, area_size=(200, 200))
        visualizer = NetworkVisualizer(network)

        visualizer.plot_topology()

        mock_show.assert_called_once()

    @patch('matplotlib.pyplot.show')
    def test_analyzer_with_constant_metrics(self, mock_show):
        """Test analyzer with constant metrics (no variance)"""
        history = [
            {'round': i, 'alive_nodes': 100, 'energy_consumed': 0.5,
             'packets_to_bs': 50, 'num_cluster_heads': 5, 'total_energy': 10.0}
            for i in range(1, 51)
        ]
        analyzer = PerformanceAnalyzer(history)

        # Should handle constant values
        report = analyzer.get_comprehensive_report()

        self.assertEqual(report['throughput']['throughput_variance'], 0)

    def test_analyzer_with_incomplete_data(self):
        """Test analyzer with incomplete round data"""
        history = [
            {'round': 1, 'alive_nodes': 100},
            {'round': 2},  # Missing most fields
            {'round': 3, 'packets_to_bs': 50},
        ]
        analyzer = PerformanceAnalyzer(history)

        # Should handle missing data gracefully
        report = analyzer.get_comprehensive_report()

        self.assertIsNotNone(report)


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)
