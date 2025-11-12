"""
Utility functions for WSN simulation and analysis
"""

import math
import json
import csv
from datetime import datetime


def calculate_distance(point1, point2):
    """
    Calculate Euclidean distance between two points.

    Args:
        point1: Tuple (x, y) or node with x, y attributes
        point2: Tuple (x, y) or node with x, y attributes

    Returns:
        Distance in meters
    """
    x1 = point1[0] if isinstance(point1, tuple) else point1.x
    y1 = point1[1] if isinstance(point1, tuple) else point1.y
    x2 = point2[0] if isinstance(point2, tuple) else point2.x
    y2 = point2[1] if isinstance(point2, tuple) else point2.y

    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)


def calculate_network_coverage(nodes, area_width, area_height, sensing_range=10, grid_resolution=1):
    """
    Calculate percentage of area covered by sensor nodes.

    Args:
        nodes: List of sensor nodes
        area_width: Width of deployment area
        area_height: Height of deployment area
        sensing_range: Sensing range of each node
        grid_resolution: Resolution for coverage calculation

    Returns:
        Coverage percentage (0-100)
    """
    total_points = 0
    covered_points = 0

    for x in range(0, int(area_width), grid_resolution):
        for y in range(0, int(area_height), grid_resolution):
            total_points += 1
            # Check if point is covered by any alive node
            for node in nodes:
                if node.is_alive():
                    distance = math.sqrt((node.x - x)**2 + (node.y - y)**2)
                    if distance <= sensing_range:
                        covered_points += 1
                        break

    return (covered_points / total_points) * 100 if total_points > 0 else 0


def save_simulation_results(results, filename=None):
    """
    Save simulation results to JSON file.

    Args:
        results: Dictionary with simulation results
        filename: Output filename (default: auto-generated with timestamp)

    Returns:
        Path to saved file

    Raises:
        IOError: If file cannot be written
        TypeError: If results cannot be serialized to JSON
    """
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"simulation_results_{timestamp}.json"

    try:
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)
    except IOError as e:
        raise IOError(f"Failed to save results to {filename}: {e}")
    except TypeError as e:
        raise TypeError(f"Results contain non-serializable data: {e}")
    except Exception as e:
        raise Exception(f"Unexpected error saving results to {filename}: {e}")

    return filename


def export_to_csv(data, filename, headers=None):
    """
    Export data to CSV file.

    Args:
        data: List of dictionaries or list of lists
        filename: Output CSV filename
        headers: List of column headers (optional)

    Raises:
        ValueError: If data is empty or invalid
        IOError: If file cannot be written
    """
    if not data:
        raise ValueError("Cannot export empty data to CSV")

    try:
        with open(filename, 'w', newline='') as f:
            if isinstance(data[0], dict):
                # Data is list of dictionaries
                writer = csv.DictWriter(f, fieldnames=headers or data[0].keys())
                writer.writeheader()
                writer.writerows(data)
            else:
                # Data is list of lists
                writer = csv.writer(f)
                if headers:
                    writer.writerow(headers)
                writer.writerows(data)
    except IOError as e:
        raise IOError(f"Failed to write CSV to {filename}: {e}")
    except Exception as e:
        raise Exception(f"Unexpected error exporting to CSV {filename}: {e}")


def calculate_energy_efficiency(total_packets, total_energy_consumed):
    """
    Calculate energy efficiency metric.

    Args:
        total_packets: Total packets delivered
        total_energy_consumed: Total energy consumed (Joules)

    Returns:
        Packets per Joule (returns 0 if no energy consumed)
    """
    if total_energy_consumed == 0:
        return 0  # Avoid division by zero
    return total_packets / total_energy_consumed


def calculate_throughput(packets_delivered, total_rounds, round_time=20):
    """
    Calculate network throughput.

    Args:
        packets_delivered: Number of packets delivered
        total_rounds: Total number of rounds
        round_time: Duration of each round in seconds

    Returns:
        Packets per second
    """
    total_time = total_rounds * round_time
    if total_time == 0:
        return 0
    return packets_delivered / total_time


def moving_average(data, window_size=10):
    """
    Calculate moving average of data.

    Args:
        data: List of numerical values
        window_size: Size of moving window

    Returns:
        List of moving averages
    """
    if len(data) < window_size:
        return data

    result = []
    for i in range(len(data)):
        start = max(0, i - window_size + 1)
        end = i + 1
        window = data[start:end]
        result.append(sum(window) / len(window))

    return result


def find_optimal_cluster_head_percentage(num_nodes, area_size, base_station_distance):
    """
    Estimate optimal cluster head percentage based on network parameters.

    Based on analytical model from LEACH paper.

    Args:
        num_nodes: Number of nodes
        area_size: Tuple (width, height)
        base_station_distance: Average distance to base station

    Returns:
        Optimal cluster head percentage (0-1)
    """
    area = area_size[0] * area_size[1]

    # Simplified optimal percentage formula
    # k_opt = sqrt(N) / sqrt(2*pi) * sqrt(E_fs/E_mp) * (M / d_toBS^2)
    # Simplified to a practical range of 5-15%

    density = num_nodes / area

    if density > 0.01:  # High density
        return 0.05
    elif density > 0.005:  # Medium density
        return 0.08
    else:  # Low density
        return 0.10


class SimulationLogger:
    """Logger for simulation events and statistics"""

    def __init__(self, log_file=None, verbose=True):
        """
        Initialize logger.

        Args:
            log_file: Path to log file (optional)
            verbose: Print to console if True

        Raises:
            IOError: If log file cannot be created
        """
        self.log_file = log_file
        self.verbose = verbose
        self.logs = []

        if self.log_file:
            try:
                with open(self.log_file, 'w') as f:
                    f.write(f"Simulation Log - Started at {datetime.now()}\n")
                    f.write("="*60 + "\n\n")
            except IOError as e:
                raise IOError(f"Failed to create log file {self.log_file}: {e}")

    def log(self, message, level="INFO"):
        """
        Log a message.

        Args:
            message: Message to log
            level: Log level (INFO, WARNING, ERROR)

        Note:
            File write errors are silently ignored to prevent log failures
            from disrupting the simulation.
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] {message}"

        self.logs.append(log_entry)

        if self.verbose:
            print(log_entry)

        if self.log_file:
            try:
                with open(self.log_file, 'a') as f:
                    f.write(log_entry + "\n")
            except IOError:
                # Silently ignore file write errors to prevent
                # logging from disrupting the simulation
                pass

    def info(self, message):
        """Log info message"""
        self.log(message, "INFO")

    def warning(self, message):
        """Log warning message"""
        self.log(message, "WARNING")

    def error(self, message):
        """Log error message"""
        self.log(message, "ERROR")

    def get_logs(self):
        """Get all logs"""
        return self.logs
