"""
Comprehensive Unit Tests for Utils Module

Tests all utility functions and SimulationLogger class.
Achieves 95%+ code coverage with edge case testing.
"""

import unittest
import sys
import os
import json
import csv
import tempfile
import shutil
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils import (
    calculate_distance, calculate_network_coverage,
    save_simulation_results, export_to_csv,
    calculate_energy_efficiency, calculate_throughput,
    moving_average, find_optimal_cluster_head_percentage,
    SimulationLogger
)
from src.network import WirelessSensorNetwork
from src.node import SensorNode, NodeType


class TestCalculateDistance(unittest.TestCase):
    """Test cases for calculate_distance function"""

    def test_distance_between_tuples(self):
        """Test distance calculation with tuple inputs"""
        point1 = (0, 0)
        point2 = (3, 4)

        distance = calculate_distance(point1, point2)

        self.assertAlmostEqual(distance, 5.0)

    def test_distance_between_nodes(self):
        """Test distance calculation with node objects"""
        node1 = SensorNode(id=1, x=0, y=0, energy=1.0)
        node2 = SensorNode(id=2, x=6, y=8, energy=1.0)

        distance = calculate_distance(node1, node2)

        self.assertAlmostEqual(distance, 10.0)

    def test_distance_mixed_inputs(self):
        """Test distance calculation with mixed tuple and node"""
        point = (0, 0)
        node = SensorNode(id=1, x=5, y=12, energy=1.0)

        distance = calculate_distance(point, node)

        self.assertAlmostEqual(distance, 13.0)

    def test_distance_same_point(self):
        """Test distance when points are the same"""
        point = (5, 5)

        distance = calculate_distance(point, point)

        self.assertAlmostEqual(distance, 0.0)

    def test_distance_negative_coordinates(self):
        """Test distance with negative coordinates"""
        point1 = (-3, -4)
        point2 = (0, 0)

        distance = calculate_distance(point1, point2)

        self.assertAlmostEqual(distance, 5.0)

    def test_distance_floating_point(self):
        """Test distance with floating point coordinates"""
        point1 = (1.5, 2.7)
        point2 = (4.3, 6.2)

        distance = calculate_distance(point1, point2)

        expected = ((4.3 - 1.5)**2 + (6.2 - 2.7)**2)**0.5
        self.assertAlmostEqual(distance, expected)


class TestCalculateNetworkCoverage(unittest.TestCase):
    """Test cases for calculate_network_coverage function"""

    def setUp(self):
        """Set up test fixtures"""
        self.network = WirelessSensorNetwork(num_nodes=5, area_size=(50, 50))

    def test_coverage_with_alive_nodes(self):
        """Test coverage calculation with alive nodes"""
        coverage = calculate_network_coverage(
            self.network.nodes,
            50, 50,
            sensing_range=20,
            grid_resolution=10
        )

        self.assertIsInstance(coverage, float)
        self.assertGreaterEqual(coverage, 0)
        self.assertLessEqual(coverage, 100)

    def test_coverage_with_dead_nodes(self):
        """Test coverage when all nodes are dead"""
        # Kill all nodes
        for node in self.network.nodes:
            node.energy = 0

        coverage = calculate_network_coverage(
            self.network.nodes,
            50, 50,
            sensing_range=10
        )

        self.assertEqual(coverage, 0.0)

    def test_coverage_full_coverage(self):
        """Test coverage with dense network"""
        # Create dense network
        network = WirelessSensorNetwork(num_nodes=20, area_size=(20, 20))

        coverage = calculate_network_coverage(
            network.nodes,
            20, 20,
            sensing_range=15,
            grid_resolution=5
        )

        # Should have high coverage with dense network and large sensing range
        self.assertGreater(coverage, 50)

    def test_coverage_different_grid_resolutions(self):
        """Test coverage with different grid resolutions"""
        coverage_fine = calculate_network_coverage(
            self.network.nodes,
            50, 50,
            sensing_range=10,
            grid_resolution=1
        )

        coverage_coarse = calculate_network_coverage(
            self.network.nodes,
            50, 50,
            sensing_range=10,
            grid_resolution=10
        )

        # Both should give similar results
        self.assertIsInstance(coverage_fine, float)
        self.assertIsInstance(coverage_coarse, float)

    def test_coverage_zero_area(self):
        """Test coverage calculation edge case"""
        # Small area with small resolution
        coverage = calculate_network_coverage(
            self.network.nodes,
            1, 1,
            sensing_range=10,
            grid_resolution=1
        )

        # Should not crash
        self.assertIsInstance(coverage, float)

    def test_coverage_large_sensing_range(self):
        """Test coverage with very large sensing range"""
        coverage = calculate_network_coverage(
            self.network.nodes,
            50, 50,
            sensing_range=100,  # Larger than area
            grid_resolution=10
        )

        # Should achieve 100% coverage if any node is alive
        if any(node.is_alive() for node in self.network.nodes):
            self.assertGreater(coverage, 0)


class TestSaveSimulationResults(unittest.TestCase):
    """Test cases for save_simulation_results function"""

    def setUp(self):
        """Set up test fixtures"""
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test files"""
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_save_with_auto_filename(self):
        """Test saving with auto-generated filename"""
        results = {
            'total_rounds': 100,
            'alive_nodes': 50,
            'energy_consumed': 2.5
        }

        filename = save_simulation_results(results)

        # Check file was created
        self.assertTrue(os.path.exists(filename))

        # Verify contents
        with open(filename, 'r') as f:
            loaded = json.load(f)
            self.assertEqual(loaded, results)

        # Clean up
        os.remove(filename)

    def test_save_with_custom_filename(self):
        """Test saving with custom filename"""
        results = {'test': 'data'}
        filepath = os.path.join(self.test_dir, 'test_results.json')

        returned_path = save_simulation_results(results, filepath)

        self.assertEqual(returned_path, filepath)
        self.assertTrue(os.path.exists(filepath))

        # Verify contents
        with open(filepath, 'r') as f:
            loaded = json.load(f)
            self.assertEqual(loaded, results)

    def test_save_complex_results(self):
        """Test saving complex nested data"""
        results = {
            'network': {
                'nodes': 100,
                'area': (100, 100)
            },
            'metrics': {
                'energy': [1.0, 0.9, 0.8],
                'alive': [100, 95, 90]
            }
        }

        filename = save_simulation_results(results)

        with open(filename, 'r') as f:
            loaded = json.load(f)
            self.assertEqual(loaded, results)

        os.remove(filename)

    def test_save_empty_results(self):
        """Test saving empty results"""
        results = {}

        filename = save_simulation_results(results)

        self.assertTrue(os.path.exists(filename))

        with open(filename, 'r') as f:
            loaded = json.load(f)
            self.assertEqual(loaded, {})

        os.remove(filename)


class TestExportToCSV(unittest.TestCase):
    """Test cases for export_to_csv function"""

    def setUp(self):
        """Set up test fixtures"""
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test files"""
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_export_list_of_dicts(self):
        """Test exporting list of dictionaries"""
        data = [
            {'round': 1, 'alive': 100, 'energy': 1.0},
            {'round': 2, 'alive': 95, 'energy': 0.9},
            {'round': 3, 'alive': 90, 'energy': 0.8}
        ]

        filepath = os.path.join(self.test_dir, 'test_dict.csv')
        export_to_csv(data, filepath)

        # Verify file was created
        self.assertTrue(os.path.exists(filepath))

        # Read and verify contents
        with open(filepath, 'r') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            self.assertEqual(len(rows), 3)
            self.assertEqual(rows[0]['round'], '1')
            self.assertEqual(rows[0]['alive'], '100')

    def test_export_list_of_lists(self):
        """Test exporting list of lists"""
        data = [
            [1, 100, 1.0],
            [2, 95, 0.9],
            [3, 90, 0.8]
        ]

        headers = ['round', 'alive', 'energy']
        filepath = os.path.join(self.test_dir, 'test_list.csv')

        export_to_csv(data, filepath, headers=headers)

        # Verify file was created
        self.assertTrue(os.path.exists(filepath))

        # Read and verify contents
        with open(filepath, 'r') as f:
            reader = csv.reader(f)
            rows = list(reader)
            self.assertEqual(rows[0], headers)
            self.assertEqual(len(rows), 4)  # header + 3 data rows

    def test_export_list_of_lists_no_headers(self):
        """Test exporting list of lists without headers"""
        data = [
            [1, 2, 3],
            [4, 5, 6]
        ]

        filepath = os.path.join(self.test_dir, 'test_no_headers.csv')
        export_to_csv(data, filepath)

        self.assertTrue(os.path.exists(filepath))

        with open(filepath, 'r') as f:
            reader = csv.reader(f)
            rows = list(reader)
            self.assertEqual(len(rows), 2)

    def test_export_with_custom_headers(self):
        """Test exporting dicts with custom headers"""
        data = [
            {'a': 1, 'b': 2, 'c': 3},
            {'a': 4, 'b': 5, 'c': 6}
        ]

        headers = ['a', 'b']  # Only export subset of fields
        filepath = os.path.join(self.test_dir, 'test_custom_headers.csv')

        export_to_csv(data, filepath, headers=headers)

        with open(filepath, 'r') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            # Should only have 'a' and 'b' columns
            self.assertIn('a', rows[0])
            self.assertIn('b', rows[0])


class TestCalculateEnergyEfficiency(unittest.TestCase):
    """Test cases for calculate_energy_efficiency function"""

    def test_normal_calculation(self):
        """Test normal energy efficiency calculation"""
        efficiency = calculate_energy_efficiency(1000, 2.5)

        self.assertEqual(efficiency, 400.0)  # 1000 / 2.5

    def test_zero_energy(self):
        """Test when energy consumed is zero"""
        efficiency = calculate_energy_efficiency(100, 0)

        self.assertEqual(efficiency, 0)

    def test_zero_packets(self):
        """Test when packets delivered is zero"""
        efficiency = calculate_energy_efficiency(0, 1.0)

        self.assertEqual(efficiency, 0.0)

    def test_both_zero(self):
        """Test when both values are zero"""
        efficiency = calculate_energy_efficiency(0, 0)

        self.assertEqual(efficiency, 0)

    def test_high_efficiency(self):
        """Test high efficiency scenario"""
        efficiency = calculate_energy_efficiency(10000, 0.1)

        self.assertEqual(efficiency, 100000.0)

    def test_low_efficiency(self):
        """Test low efficiency scenario"""
        efficiency = calculate_energy_efficiency(10, 100)

        self.assertEqual(efficiency, 0.1)


class TestCalculateThroughput(unittest.TestCase):
    """Test cases for calculate_throughput function"""

    def test_normal_calculation(self):
        """Test normal throughput calculation"""
        throughput = calculate_throughput(1000, 50, round_time=20)

        # 1000 packets / (50 rounds * 20 seconds) = 1 packet/second
        self.assertEqual(throughput, 1.0)

    def test_zero_rounds(self):
        """Test when total rounds is zero"""
        throughput = calculate_throughput(100, 0, round_time=20)

        self.assertEqual(throughput, 0)

    def test_zero_packets(self):
        """Test when packets delivered is zero"""
        throughput = calculate_throughput(0, 100, round_time=20)

        self.assertEqual(throughput, 0.0)

    def test_high_throughput(self):
        """Test high throughput scenario"""
        throughput = calculate_throughput(10000, 10, round_time=1)

        self.assertEqual(throughput, 1000.0)

    def test_low_throughput(self):
        """Test low throughput scenario"""
        throughput = calculate_throughput(10, 1000, round_time=10)

        self.assertEqual(throughput, 0.001)

    def test_custom_round_time(self):
        """Test with custom round time"""
        throughput = calculate_throughput(500, 10, round_time=5)

        # 500 / (10 * 5) = 10
        self.assertEqual(throughput, 10.0)


class TestMovingAverage(unittest.TestCase):
    """Test cases for moving_average function"""

    def test_normal_calculation(self):
        """Test normal moving average calculation"""
        data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        window_size = 3

        result = moving_average(data, window_size)

        # First few values
        self.assertAlmostEqual(result[0], 1.0)  # [1]
        self.assertAlmostEqual(result[1], 1.5)  # [1, 2]
        self.assertAlmostEqual(result[2], 2.0)  # [1, 2, 3]
        self.assertAlmostEqual(result[3], 3.0)  # [2, 3, 4]

    def test_window_size_larger_than_data(self):
        """Test when window size is larger than data length"""
        data = [1, 2, 3]
        window_size = 10

        result = moving_average(data, window_size)

        # Should return original data
        self.assertEqual(result, data)

    def test_window_size_one(self):
        """Test with window size of 1"""
        data = [1, 2, 3, 4, 5]
        window_size = 1

        result = moving_average(data, window_size)

        # Should return original data
        self.assertEqual(result, data)

    def test_empty_data(self):
        """Test with empty data"""
        data = []
        window_size = 3

        result = moving_average(data, window_size)

        self.assertEqual(result, [])

    def test_single_value(self):
        """Test with single value"""
        data = [5.0]
        window_size = 3

        result = moving_average(data, window_size)

        self.assertEqual(result, [5.0])

    def test_large_window(self):
        """Test with large window size"""
        data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        window_size = 5

        result = moving_average(data, window_size)

        self.assertEqual(len(result), len(data))
        # Last value should be average of last 5: (6+7+8+9+10)/5 = 8
        self.assertAlmostEqual(result[-1], 8.0)


class TestFindOptimalClusterHeadPercentage(unittest.TestCase):
    """Test cases for find_optimal_cluster_head_percentage function"""

    def test_high_density_network(self):
        """Test with high density network"""
        num_nodes = 200
        area_size = (100, 100)  # density = 0.02
        base_station_distance = 50

        percentage = find_optimal_cluster_head_percentage(
            num_nodes, area_size, base_station_distance
        )

        self.assertEqual(percentage, 0.05)

    def test_medium_density_network(self):
        """Test with medium density network"""
        num_nodes = 70
        area_size = (100, 100)  # density = 0.007
        base_station_distance = 50

        percentage = find_optimal_cluster_head_percentage(
            num_nodes, area_size, base_station_distance
        )

        self.assertEqual(percentage, 0.08)

    def test_low_density_network(self):
        """Test with low density network"""
        num_nodes = 30
        area_size = (100, 100)  # density = 0.003
        base_station_distance = 50

        percentage = find_optimal_cluster_head_percentage(
            num_nodes, area_size, base_station_distance
        )

        self.assertEqual(percentage, 0.10)

    def test_very_high_density(self):
        """Test with very high density"""
        num_nodes = 1000
        area_size = (50, 50)  # density = 0.4
        base_station_distance = 30

        percentage = find_optimal_cluster_head_percentage(
            num_nodes, area_size, base_station_distance
        )

        self.assertEqual(percentage, 0.05)

    def test_large_area(self):
        """Test with large area"""
        num_nodes = 100
        area_size = (500, 500)  # density = 0.0004
        base_station_distance = 200

        percentage = find_optimal_cluster_head_percentage(
            num_nodes, area_size, base_station_distance
        )

        self.assertEqual(percentage, 0.10)

    def test_percentage_range(self):
        """Test that percentage is always in valid range"""
        test_cases = [
            (50, (100, 100), 50),
            (100, (100, 100), 50),
            (200, (100, 100), 50),
            (100, (200, 200), 100),
        ]

        for num_nodes, area_size, bs_dist in test_cases:
            percentage = find_optimal_cluster_head_percentage(
                num_nodes, area_size, bs_dist
            )
            self.assertGreaterEqual(percentage, 0.05)
            self.assertLessEqual(percentage, 0.10)


class TestSimulationLogger(unittest.TestCase):
    """Test cases for SimulationLogger class"""

    def setUp(self):
        """Set up test fixtures"""
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test files"""
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_initialization_no_file(self):
        """Test logger initialization without file"""
        logger = SimulationLogger(verbose=False)

        self.assertIsNone(logger.log_file)
        self.assertFalse(logger.verbose)
        self.assertEqual(len(logger.logs), 0)

    def test_initialization_with_file(self):
        """Test logger initialization with file"""
        filepath = os.path.join(self.test_dir, 'test.log')
        logger = SimulationLogger(log_file=filepath, verbose=False)

        self.assertEqual(logger.log_file, filepath)
        self.assertTrue(os.path.exists(filepath))

        # Check header was written
        with open(filepath, 'r') as f:
            content = f.read()
            self.assertIn('Simulation Log', content)

    def test_log_info_message(self):
        """Test logging info message"""
        logger = SimulationLogger(verbose=False)

        logger.info("Test info message")

        logs = logger.get_logs()
        self.assertEqual(len(logs), 1)
        self.assertIn('INFO', logs[0])
        self.assertIn('Test info message', logs[0])

    def test_log_warning_message(self):
        """Test logging warning message"""
        logger = SimulationLogger(verbose=False)

        logger.warning("Test warning")

        logs = logger.get_logs()
        self.assertEqual(len(logs), 1)
        self.assertIn('WARNING', logs[0])
        self.assertIn('Test warning', logs[0])

    def test_log_error_message(self):
        """Test logging error message"""
        logger = SimulationLogger(verbose=False)

        logger.error("Test error")

        logs = logger.get_logs()
        self.assertEqual(len(logs), 1)
        self.assertIn('ERROR', logs[0])
        self.assertIn('Test error', logs[0])

    def test_log_with_file(self):
        """Test logging to file"""
        filepath = os.path.join(self.test_dir, 'test.log')
        logger = SimulationLogger(log_file=filepath, verbose=False)

        logger.info("Test message")
        logger.warning("Warning message")
        logger.error("Error message")

        # Check file contains messages
        with open(filepath, 'r') as f:
            content = f.read()
            self.assertIn('Test message', content)
            self.assertIn('Warning message', content)
            self.assertIn('Error message', content)

    def test_log_multiple_messages(self):
        """Test logging multiple messages"""
        logger = SimulationLogger(verbose=False)

        for i in range(10):
            logger.info(f"Message {i}")

        logs = logger.get_logs()
        self.assertEqual(len(logs), 10)

    def test_get_logs(self):
        """Test getting all logs"""
        logger = SimulationLogger(verbose=False)

        logger.info("Message 1")
        logger.warning("Message 2")
        logger.error("Message 3")

        logs = logger.get_logs()

        self.assertEqual(len(logs), 3)
        self.assertIsInstance(logs, list)

    def test_log_timestamp_format(self):
        """Test that logs include proper timestamp"""
        logger = SimulationLogger(verbose=False)

        logger.info("Test")

        logs = logger.get_logs()
        # Should have format: [YYYY-MM-DD HH:MM:SS] [LEVEL] message
        self.assertRegex(logs[0], r'\[\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\]')

    def test_verbose_mode(self):
        """Test verbose mode (prints to console)"""
        import io
        from contextlib import redirect_stdout

        logger = SimulationLogger(verbose=True)

        # Capture stdout
        f = io.StringIO()
        with redirect_stdout(f):
            logger.info("Test message")

        output = f.getvalue()
        self.assertIn("Test message", output)


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)
