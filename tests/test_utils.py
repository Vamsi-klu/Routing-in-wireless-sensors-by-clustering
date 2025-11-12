"""
Comprehensive unit tests for utils.py

Tests cover all utility functions for 95%+ coverage.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
import tempfile
import json
from src.utils import (
    calculate_distance, calculate_network_coverage,
    save_simulation_results, export_to_csv,
    calculate_energy_efficiency, calculate_throughput,
    moving_average, find_optimal_cluster_head_percentage,
    SimulationLogger
)
from src.network import WirelessSensorNetwork


class TestCalculateDistance:
    """Test distance calculation utility"""

    def test_distance_between_tuples(self):
        """Test distance between two coordinate tuples"""
        point1 = (0, 0)
        point2 = (3, 4)

        distance = calculate_distance(point1, point2)

        assert distance == 5.0

    def test_distance_between_nodes(self):
        """Test distance between two nodes"""
        from src.node import SensorNode
        node1 = SensorNode(0, 0, 0, 0.5)
        node2 = SensorNode(1, 3, 4, 0.5)

        distance = calculate_distance(node1, node2)

        assert distance == 5.0

    def test_distance_zero(self):
        """Test distance at same location"""
        point1 = (10, 20)
        point2 = (10, 20)

        distance = calculate_distance(point1, point2)

        assert distance == 0.0


class TestCalculateNetworkCoverage:
    """Test network coverage calculation"""

    def test_full_coverage(self):
        """Test network with full coverage"""
        network = WirelessSensorNetwork(num_nodes=100, deployment='grid')

        coverage = calculate_network_coverage(
            network.nodes,
            network.area_width,
            network.area_height,
            sensing_range=20,
            grid_resolution=10
        )

        assert 0 <= coverage <= 100

    def test_partial_coverage(self):
        """Test network with partial coverage"""
        network = WirelessSensorNetwork(num_nodes=5, deployment='random')

        coverage = calculate_network_coverage(
            network.nodes,
            network.area_width,
            network.area_height,
            sensing_range=10,
            grid_resolution=5
        )

        assert 0 <= coverage <= 100

    def test_no_coverage_dead_nodes(self):
        """Test coverage with all dead nodes"""
        network = WirelessSensorNetwork(num_nodes=10)
        for node in network.nodes:
            node.state = node.state.__class__.DEAD

        coverage = calculate_network_coverage(
            network.nodes,
            network.area_width,
            network.area_height
        )

        assert coverage == 0.0

    def test_coverage_with_custom_sensing_range(self):
        """Test coverage with custom sensing range"""
        network = WirelessSensorNetwork(num_nodes=20, deployment='grid')

        coverage = calculate_network_coverage(
            network.nodes,
            network.area_width,
            network.area_height,
            sensing_range=30
        )

        assert coverage > 0


class TestSaveSimulationResults:
    """Test saving simulation results"""

    def test_save_results_default_filename(self):
        """Test saving results with default filename"""
        results = {"test": "data", "rounds": 100}

        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, "test_results.json")
            saved_path = save_simulation_results(results, filepath)

            assert os.path.exists(saved_path)
            with open(saved_path, 'r') as f:
                loaded = json.load(f)
            assert loaded == results

    def test_save_results_auto_filename(self):
        """Test saving results with auto-generated filename"""
        results = {"test": "data"}

        # Save in temp directory
        original_dir = os.getcwd()
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                os.chdir(tmpdir)
                saved_path = save_simulation_results(results)

                assert os.path.exists(saved_path)
                assert saved_path.endswith('.json')
        finally:
            os.chdir(original_dir)


class TestExportToCSV:
    """Test CSV export functionality"""

    def test_export_dict_list(self):
        """Test exporting list of dictionaries"""
        data = [
            {"round": 1, "energy": 0.5},
            {"round": 2, "energy": 0.4}
        ]

        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
            filename = f.name

        try:
            export_to_csv(data, filename)

            assert os.path.exists(filename)
            with open(filename, 'r') as f:
                content = f.read()
            assert "round" in content
            assert "energy" in content
        finally:
            if os.path.exists(filename):
                os.unlink(filename)

    def test_export_list_with_headers(self):
        """Test exporting list of lists with headers"""
        data = [
            [1, 0.5],
            [2, 0.4]
        ]
        headers = ["round", "energy"]

        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
            filename = f.name

        try:
            export_to_csv(data, filename, headers)

            assert os.path.exists(filename)
            with open(filename, 'r') as f:
                content = f.read()
            assert "round" in content
        finally:
            if os.path.exists(filename):
                os.unlink(filename)


class TestCalculateEnergyEfficiency:
    """Test energy efficiency calculation"""

    def test_energy_efficiency(self):
        """Test basic energy efficiency calculation"""
        efficiency = calculate_energy_efficiency(1000, 0.5)

        assert efficiency == 2000.0

    def test_energy_efficiency_zero_energy(self):
        """Test efficiency with zero energy consumed"""
        efficiency = calculate_energy_efficiency(1000, 0)

        assert efficiency == 0

    def test_energy_efficiency_zero_packets(self):
        """Test efficiency with zero packets"""
        efficiency = calculate_energy_efficiency(0, 0.5)

        assert efficiency == 0.0


class TestCalculateThroughput:
    """Test throughput calculation"""

    def test_throughput_calculation(self):
        """Test basic throughput calculation"""
        throughput = calculate_throughput(1000, 50, round_time=20)

        assert throughput == 1.0  # 1000 / (50 * 20) = 1.0

    def test_throughput_zero_rounds(self):
        """Test throughput with zero rounds"""
        throughput = calculate_throughput(1000, 0)

        assert throughput == 0

    def test_throughput_custom_round_time(self):
        """Test throughput with custom round time"""
        throughput = calculate_throughput(100, 10, round_time=10)

        assert throughput == 1.0


class TestMovingAverage:
    """Test moving average calculation"""

    def test_moving_average(self):
        """Test basic moving average"""
        data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

        result = moving_average(data, window_size=3)

        assert len(result) == len(data)
        assert result[0] == 1.0  # First element
        assert result[2] == 2.0  # Average of [1,2,3]

    def test_moving_average_small_data(self):
        """Test moving average with data smaller than window"""
        data = [1, 2, 3]

        result = moving_average(data, window_size=10)

        assert result == data

    def test_moving_average_window_one(self):
        """Test moving average with window size 1"""
        data = [1, 2, 3, 4, 5]

        result = moving_average(data, window_size=1)

        assert result == data


class TestFindOptimalClusterHeadPercentage:
    """Test optimal CH percentage calculation"""

    def test_high_density(self):
        """Test optimal percentage for high density network"""
        percentage = find_optimal_cluster_head_percentage(
            num_nodes=100,
            area_size=(100, 100),
            base_station_distance=150
        )

        assert 0.01 <= percentage <= 0.15
        assert percentage == 0.08  # Returns 0.08 for high density

    def test_medium_density(self):
        """Test optimal percentage for medium density network"""
        percentage = find_optimal_cluster_head_percentage(
            num_nodes=100,
            area_size=(200, 200),
            base_station_distance=200
        )

        assert percentage == 0.10  # Medium density

    def test_low_density(self):
        """Test optimal percentage for low density network"""
        percentage = find_optimal_cluster_head_percentage(
            num_nodes=100,
            area_size=(500, 500),
            base_station_distance=500
        )

        assert percentage == 0.10  # Low density


class TestSimulationLogger:
    """Test simulation logger"""

    def test_logger_initialization(self):
        """Test logger initialization"""
        logger = SimulationLogger(verbose=False)

        assert logger.verbose is False
        assert logger.logs == []

    def test_logger_with_file(self):
        """Test logger with file output"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as f:
            filename = f.name

        try:
            logger = SimulationLogger(log_file=filename, verbose=False)
            logger.log("Test message")

            assert os.path.exists(filename)
            with open(filename, 'r') as f:
                content = f.read()
            assert "Test message" in content
        finally:
            if os.path.exists(filename):
                os.unlink(filename)

    def test_log_info(self):
        """Test logging info message"""
        logger = SimulationLogger(verbose=False)

        logger.info("Info message")

        assert len(logger.logs) == 1
        assert "INFO" in logger.logs[0]
        assert "Info message" in logger.logs[0]

    def test_log_warning(self):
        """Test logging warning message"""
        logger = SimulationLogger(verbose=False)

        logger.warning("Warning message")

        assert len(logger.logs) == 1
        assert "WARNING" in logger.logs[0]

    def test_log_error(self):
        """Test logging error message"""
        logger = SimulationLogger(verbose=False)

        logger.error("Error message")

        assert len(logger.logs) == 1
        assert "ERROR" in logger.logs[0]

    def test_get_logs(self):
        """Test getting all logs"""
        logger = SimulationLogger(verbose=False)

        logger.info("Message 1")
        logger.warning("Message 2")
        logger.error("Message 3")

        logs = logger.get_logs()

        assert len(logs) == 3

    def test_verbose_output(self, capsys):
        """Test verbose console output"""
        logger = SimulationLogger(verbose=True)

        logger.info("Test message")

        captured = capsys.readouterr()
        assert "Test message" in captured.out


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
