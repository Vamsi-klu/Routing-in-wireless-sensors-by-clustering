"""
Sensor Node Implementation for Wireless Sensor Networks

Represents individual sensor nodes with energy management,
communication capabilities, and clustering support.
"""

import math
from enum import Enum
from src.energy_model import default_energy_model


class NodeType(Enum):
    """Node types in the network"""
    NORMAL = "normal"
    CLUSTER_HEAD = "cluster_head"
    BASE_STATION = "base_station"


class NodeState(Enum):
    """Node operational states"""
    ACTIVE = "active"
    SLEEP = "sleep"
    DEAD = "dead"


class SensorNode:
    """
    Represents a sensor node in a wireless sensor network.

    Attributes:
        id: Unique node identifier
        x, y: Node coordinates
        initial_energy: Initial energy in Joules
        energy: Current remaining energy
        node_type: Current role (normal, cluster_head, base_station)
        state: Current operational state
    """

    def __init__(self, node_id, x, y, initial_energy=0.5, energy_model=None):
        """
        Initialize a sensor node.

        Args:
            node_id: Unique identifier
            x: X-coordinate
            y: Y-coordinate
            initial_energy: Initial energy in Joules (default: 0.5 J)
            energy_model: Energy model to use (default: default_energy_model)
        """
        self.id = node_id
        self.x = x
        self.y = y
        self.initial_energy = initial_energy
        self.energy = initial_energy
        self.energy_model = energy_model or default_energy_model

        # Node role and state
        self.node_type = NodeType.NORMAL
        self.state = NodeState.ACTIVE

        # Clustering information
        self.cluster_head = None  # Reference to cluster head
        self.cluster_members = []  # List of cluster members (if CH)
        self.is_cluster_head = False
        self.ch_rounds = 0  # Number of rounds as CH

        # Communication statistics
        self.packets_sent = 0
        self.packets_received = 0
        self.total_tx_distance = 0.0

        # Round information
        self.last_ch_round = -1  # Last round when node was CH
        self.round = 0

    def distance_to(self, other_node):
        """
        Calculate Euclidean distance to another node.

        Args:
            other_node: Target node or (x, y) tuple

        Returns:
            Distance in meters
        """
        if isinstance(other_node, tuple):
            target_x, target_y = other_node
        else:
            target_x, target_y = other_node.x, other_node.y

        return math.sqrt((self.x - target_x) ** 2 + (self.y - target_y) ** 2)

    def is_alive(self):
        """Check if node has remaining energy"""
        return self.energy > 0 and self.state != NodeState.DEAD

    def is_dead(self):
        """Check if node is dead"""
        return self.energy <= 0 or self.state == NodeState.DEAD

    def transmit(self, destination, num_bits=None):
        """
        Transmit data to a destination node.

        Args:
            destination: Destination node or (x, y) tuple
            num_bits: Number of bits to transmit

        Returns:
            True if successful, False if insufficient energy
        """
        if not self.is_alive():
            return False

        distance = self.distance_to(destination)
        energy_required = self.energy_model.transmit_energy(distance, num_bits)

        if self.energy >= energy_required:
            self.energy -= energy_required
            self.packets_sent += 1
            self.total_tx_distance += distance

            if self.energy <= 0:
                self.state = NodeState.DEAD

            return True
        else:
            self.state = NodeState.DEAD
            self.energy = 0
            return False

    def receive(self, num_bits=None):
        """
        Receive data.

        Args:
            num_bits: Number of bits to receive

        Returns:
            True if successful, False if insufficient energy
        """
        if not self.is_alive():
            return False

        energy_required = self.energy_model.receive_energy(num_bits)

        if self.energy >= energy_required:
            self.energy -= energy_required
            self.packets_received += 1

            if self.energy <= 0:
                self.state = NodeState.DEAD

            return True
        else:
            self.state = NodeState.DEAD
            self.energy = 0
            return False

    def aggregate_data(self, num_packets):
        """
        Aggregate data from multiple sources.

        Args:
            num_packets: Number of packets to aggregate

        Returns:
            True if successful, False if insufficient energy
        """
        if not self.is_alive():
            return False

        energy_required = self.energy_model.aggregate_energy(num_packets)

        if self.energy >= energy_required:
            self.energy -= energy_required

            if self.energy <= 0:
                self.state = NodeState.DEAD

            return True
        else:
            self.state = NodeState.DEAD
            self.energy = 0
            return False

    def sense(self):
        """
        Perform sensing operation.

        Returns:
            True if successful, False if insufficient energy
        """
        if not self.is_alive():
            return False

        energy_required = self.energy_model.sensing_energy()

        if self.energy >= energy_required:
            self.energy -= energy_required

            if self.energy <= 0:
                self.state = NodeState.DEAD

            return True
        else:
            self.state = NodeState.DEAD
            self.energy = 0
            return False

    def set_cluster_head(self, is_ch=True):
        """
        Set node as cluster head or normal node.

        Args:
            is_ch: True to set as cluster head, False for normal node
        """
        self.is_cluster_head = is_ch
        self.node_type = NodeType.CLUSTER_HEAD if is_ch else NodeType.NORMAL

        if is_ch:
            self.cluster_members = []
            self.cluster_head = self
            self.ch_rounds += 1
            self.last_ch_round = self.round
        else:
            self.cluster_members = []
            self.cluster_head = None

    def join_cluster(self, cluster_head):
        """
        Join a cluster by associating with a cluster head.

        Args:
            cluster_head: The cluster head node to join
        """
        self.cluster_head = cluster_head
        self.is_cluster_head = False
        self.node_type = NodeType.NORMAL

    def get_energy_percentage(self):
        """
        Get remaining energy as percentage of initial energy.

        Returns:
            Energy percentage (0-100)
        """
        if self.initial_energy == 0:
            return 0
        return (self.energy / self.initial_energy) * 100

    def reset_for_new_round(self):
        """Reset node state for a new round"""
        self.round += 1
        if not self.is_cluster_head:
            self.cluster_head = None
            self.cluster_members = []

    def __str__(self):
        """String representation of the node"""
        return (f"Node {self.id}: ({self.x:.1f}, {self.y:.1f}), "
                f"Energy: {self.energy:.4f}J ({self.get_energy_percentage():.1f}%), "
                f"Type: {self.node_type.value}, State: {self.state.value}")

    def __repr__(self):
        return f"SensorNode(id={self.id}, pos=({self.x}, {self.y}), energy={self.energy:.4f})"
