"""
Wireless Sensor Network Simulation Engine

Manages the overall network topology, node deployment,
and provides network-level operations and statistics.
"""

import random
import numpy as np
from src.node import SensorNode, NodeType
from src.energy_model import EnergyModel


class WirelessSensorNetwork:
    """
    Wireless Sensor Network simulation environment.

    Manages network topology, node deployment, and provides
    interfaces for protocol implementations and analysis.
    """

    def __init__(self,
                 num_nodes=100,
                 area_size=(100, 100),
                 base_station=(50, 150),
                 initial_energy=0.5,
                 energy_model=None,
                 deployment='random',
                 random_seed=None):
        """
        Initialize wireless sensor network.

        Args:
            num_nodes: Number of sensor nodes
            area_size: Tuple (width, height) of deployment area in meters
            base_station: Tuple (x, y) coordinates of base station
            initial_energy: Initial energy per node in Joules
            energy_model: Energy model to use (default: creates new EnergyModel)
            deployment: Deployment strategy ('random', 'grid', 'cluster')
            random_seed: Random seed for reproducibility (default: None for random behavior)

        Raises:
            ValueError: If parameters are invalid
            TypeError: If parameters have incorrect types
        """
        # Validate num_nodes
        if not isinstance(num_nodes, int):
            raise TypeError("num_nodes must be an integer")
        if num_nodes <= 0:
            raise ValueError("num_nodes must be positive")

        # Validate area_size
        if not isinstance(area_size, tuple) or len(area_size) != 2:
            raise ValueError("area_size must be a tuple of (width, height)")
        if area_size[0] <= 0 or area_size[1] <= 0:
            raise ValueError("area dimensions must be positive")

        # Validate base_station
        if not isinstance(base_station, tuple) or len(base_station) != 2:
            raise ValueError("base_station must be a tuple of (x, y) coordinates")

        # Validate initial_energy
        if initial_energy < 0:
            raise ValueError("initial_energy cannot be negative")

        # Validate deployment strategy
        valid_deployments = ['random', 'grid', 'cluster']
        if deployment not in valid_deployments:
            raise ValueError(
                f"Unknown deployment strategy: '{deployment}'. "
                f"Valid options are: {', '.join(valid_deployments)}"
            )

        self.num_nodes = num_nodes
        self.area_width, self.area_height = area_size
        self.base_station = base_station
        self.initial_energy = initial_energy
        self.energy_model = energy_model or EnergyModel()
        self.deployment = deployment
        self.random_seed = random_seed

        # Set random seed for reproducibility
        if random_seed is not None:
            random.seed(random_seed)
            np.random.seed(random_seed)

        # Network state
        self.nodes = []
        self.current_round = 0

        # Statistics tracking
        self.first_node_death_round = None
        self.half_nodes_death_round = None
        self.last_node_death_round = None

        # Initialize network
        self._deploy_nodes()

    def _deploy_nodes(self):
        """Deploy sensor nodes in the network area"""
        if self.deployment == 'random':
            self._random_deployment()
        elif self.deployment == 'grid':
            self._grid_deployment()
        elif self.deployment == 'cluster':
            self._cluster_deployment()
        else:
            # This should not happen due to validation in __init__
            valid_deployments = ['random', 'grid', 'cluster']
            raise ValueError(
                f"Unknown deployment strategy: '{self.deployment}'. "
                f"Valid options are: {', '.join(valid_deployments)}"
            )

    def _random_deployment(self):
        """Randomly deploy nodes in the area"""
        self.nodes = []
        for i in range(self.num_nodes):
            x = random.uniform(0, self.area_width)
            y = random.uniform(0, self.area_height)
            node = SensorNode(
                node_id=i,
                x=x,
                y=y,
                initial_energy=self.initial_energy,
                energy_model=self.energy_model
            )
            self.nodes.append(node)

    def _grid_deployment(self):
        """Deploy nodes in a grid pattern"""
        self.nodes = []
        grid_size = int(np.ceil(np.sqrt(self.num_nodes)))
        x_step = self.area_width / (grid_size + 1)
        y_step = self.area_height / (grid_size + 1)

        node_id = 0
        for i in range(grid_size):
            for j in range(grid_size):
                if node_id >= self.num_nodes:
                    break
                x = (i + 1) * x_step
                y = (j + 1) * y_step
                node = SensorNode(
                    node_id=node_id,
                    x=x,
                    y=y,
                    initial_energy=self.initial_energy,
                    energy_model=self.energy_model
                )
                self.nodes.append(node)
                node_id += 1

    def _cluster_deployment(self):
        """Deploy nodes in clustered pattern"""
        self.nodes = []
        num_clusters = max(3, self.num_nodes // 20)
        nodes_per_cluster = self.num_nodes // num_clusters

        # Generate cluster centers
        cluster_centers = [
            (random.uniform(0.2 * self.area_width, 0.8 * self.area_width),
             random.uniform(0.2 * self.area_height, 0.8 * self.area_height))
            for _ in range(num_clusters)
        ]

        node_id = 0
        for center_x, center_y in cluster_centers:
            for _ in range(nodes_per_cluster):
                if node_id >= self.num_nodes:
                    break
                # Add Gaussian noise around cluster center
                x = np.clip(np.random.normal(center_x, 10), 0, self.area_width)
                y = np.clip(np.random.normal(center_y, 10), 0, self.area_height)
                node = SensorNode(
                    node_id=node_id,
                    x=x,
                    y=y,
                    initial_energy=self.initial_energy,
                    energy_model=self.energy_model
                )
                self.nodes.append(node)
                node_id += 1

    def get_alive_nodes(self):
        """Get list of alive nodes"""
        return [node for node in self.nodes if node.is_alive()]

    def get_dead_nodes(self):
        """Get list of dead nodes"""
        return [node for node in self.nodes if node.is_dead()]

    def is_dead(self):
        """Check if entire network is dead"""
        return all(node.is_dead() for node in self.nodes)

    def get_network_lifetime_stats(self):
        """
        Calculate network lifetime statistics.

        Returns:
            Dictionary with FND, HND, LND
        """
        return {
            'first_node_death': self.first_node_death_round,
            'half_nodes_death': self.half_nodes_death_round,
            'last_node_death': self.last_node_death_round,
        }

    def update_lifetime_stats(self, current_round):
        """Update network lifetime statistics"""
        dead_count = len(self.get_dead_nodes())

        # First Node Death (FND)
        if self.first_node_death_round is None and dead_count > 0:
            self.first_node_death_round = current_round

        # Half Nodes Death (HND)
        if self.half_nodes_death_round is None and dead_count >= self.num_nodes / 2:
            self.half_nodes_death_round = current_round

        # Last Node Death (LND)
        if self.last_node_death_round is None and dead_count == self.num_nodes:
            self.last_node_death_round = current_round

    def get_energy_statistics(self):
        """
        Calculate energy-related statistics.

        Returns:
            Dictionary with energy statistics
        """
        alive_nodes = self.get_alive_nodes()

        if not alive_nodes:
            return {
                'total_energy': 0,
                'avg_energy': 0,
                'min_energy': 0,
                'max_energy': 0,
                'std_energy': 0,
                'total_consumed': self.num_nodes * self.initial_energy,
                'avg_consumed_percentage': 100,
            }

        energies = [node.energy for node in alive_nodes]
        total_initial = self.num_nodes * self.initial_energy
        total_current = sum(node.energy for node in self.nodes)
        total_consumed = total_initial - total_current

        return {
            'total_energy': total_current,
            'avg_energy': np.mean(energies),
            'min_energy': min(energies),
            'max_energy': max(energies),
            'std_energy': np.std(energies),
            'total_consumed': total_consumed,
            'avg_consumed_percentage': (total_consumed / total_initial) * 100,
        }

    def get_network_statistics(self):
        """
        Get comprehensive network statistics.

        Returns:
            Dictionary with network statistics
        """
        alive_nodes = self.get_alive_nodes()
        dead_nodes = self.get_dead_nodes()
        energy_stats = self.get_energy_statistics()
        lifetime_stats = self.get_network_lifetime_stats()

        total_packets_sent = sum(node.packets_sent for node in self.nodes)
        total_packets_received = sum(node.packets_received for node in self.nodes)

        return {
            'total_nodes': self.num_nodes,
            'alive_nodes': len(alive_nodes),
            'dead_nodes': len(dead_nodes),
            'alive_percentage': (len(alive_nodes) / self.num_nodes) * 100,
            'total_packets_sent': total_packets_sent,
            'total_packets_received': total_packets_received,
            'energy': energy_stats,
            'lifetime': lifetime_stats,
        }

    def print_statistics(self):
        """Print network statistics"""
        stats = self.get_network_statistics()

        print("\n" + "="*60)
        print("NETWORK STATISTICS")
        print("="*60)
        print(f"Total Nodes: {stats['total_nodes']}")
        print(f"Alive Nodes: {stats['alive_nodes']} ({stats['alive_percentage']:.1f}%)")
        print(f"Dead Nodes: {stats['dead_nodes']}")
        print(f"\nEnergy Statistics:")
        print(f"  Total Remaining: {stats['energy']['total_energy']:.4f} J")
        print(f"  Average: {stats['energy']['avg_energy']:.4f} J")
        print(f"  Min: {stats['energy']['min_energy']:.4f} J")
        print(f"  Max: {stats['energy']['max_energy']:.4f} J")
        print(f"  Consumed: {stats['energy']['avg_consumed_percentage']:.1f}%")
        print(f"\nNetwork Lifetime:")
        print(f"  First Node Death: Round {stats['lifetime']['first_node_death']}")
        print(f"  Half Nodes Death: Round {stats['lifetime']['half_nodes_death']}")
        print(f"  Last Node Death: Round {stats['lifetime']['last_node_death']}")
        print(f"\nCommunication:")
        print(f"  Total Packets Sent: {stats['total_packets_sent']}")
        print(f"  Total Packets Received: {stats['total_packets_received']}")
        print("="*60)

    def reset(self):
        """Reset network to initial state"""
        from src.node import NodeState

        for node in self.nodes:
            node.energy = node.initial_energy
            node.state = NodeState.ACTIVE
            node.node_type = NodeType.NORMAL
            node.packets_sent = 0
            node.packets_received = 0
            node.is_cluster_head = False
            node.cluster_head = None
            node.cluster_members = []
            node.ch_rounds = 0
            node.last_ch_round = -1
            node.round = 0

        self.current_round = 0
        self.first_node_death_round = None
        self.half_nodes_death_round = None
        self.last_node_death_round = None

    def __str__(self):
        alive = len(self.get_alive_nodes())
        return f"WSN: {alive}/{self.num_nodes} nodes alive, Area: {self.area_width}x{self.area_height}m"
