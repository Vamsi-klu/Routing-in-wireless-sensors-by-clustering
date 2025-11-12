"""
LEACH (Low Energy Adaptive Clustering Hierarchy) Protocol Implementation

LEACH is a hierarchical clustering protocol for wireless sensor networks
that uses randomized rotation of cluster heads to distribute energy load.

Protocol Phases:
1. Setup Phase: Cluster head election and cluster formation
2. Steady-State Phase: Data transmission and aggregation

Reference:
Heinzelman, W.R., Chandrakasan, A., & Balakrishnan, H. (2000).
Energy-efficient communication protocol for wireless microsensor networks.
"""

import random
import math
from src.node import NodeType


class LEACH:
    """
    LEACH clustering protocol implementation.

    The protocol operates in rounds, each consisting of:
    - Setup phase: CH election and cluster formation
    - Steady-state phase: Data collection and transmission
    """

    def __init__(self, network, cluster_head_probability=0.05, round_time=20):
        """
        Initialize LEACH protocol.

        Args:
            network: WirelessSensorNetwork instance
            cluster_head_probability: Desired percentage of cluster heads (default: 5%)
            round_time: Duration of each round in time units
        """
        self.network = network
        self.p = cluster_head_probability  # Optimal percentage of CHs
        self.round_time = round_time
        self.current_round = 0
        self.cluster_heads = []
        self.clusters = {}  # CH_id -> [member nodes]

        # Statistics
        self.total_packets_to_bs = 0
        self.total_energy_consumed = 0
        self.rounds_history = []

    def run_round(self):
        """
        Execute one complete round of LEACH protocol.

        Returns:
            Dictionary with round statistics
        """
        self.current_round += 1

        # Setup phase
        self.setup_phase()

        # Steady-state phase
        stats = self.steady_state_phase()

        # Record statistics
        self.rounds_history.append(stats)

        return stats

    def setup_phase(self):
        """
        Setup phase: Cluster head election and cluster formation.

        Steps:
        1. Each node decides to be CH based on threshold
        2. CHs broadcast advertisement
        3. Non-CH nodes join nearest CH
        4. CHs create TDMA schedule
        """
        # Reset previous round clustering
        self.cluster_heads = []
        self.clusters = {}

        # Step 1: Cluster Head Election
        self._elect_cluster_heads()

        # Step 2: Cluster Formation
        if self.cluster_heads:
            self._form_clusters()
        else:
            # If no CHs elected, force election
            self._force_cluster_head_election()
            if self.cluster_heads:
                self._form_clusters()

    def _elect_cluster_heads(self):
        """
        Elect cluster heads based on LEACH threshold function.

        Threshold T(n) = p / (1 - p * (r mod (1/p))) if n ∈ G, else 0
        where:
        - p: desired percentage of cluster heads
        - r: current round
        - G: set of nodes that haven't been CH in last 1/p rounds
        """
        alive_nodes = [node for node in self.network.nodes if node.is_alive()]

        if not alive_nodes:
            return

        # Calculate the rotation period
        rotation_period = int(1 / self.p) if self.p > 0 else 1

        for node in alive_nodes:
            # Check if node was CH recently
            rounds_since_ch = self.current_round - node.last_ch_round

            # Node is eligible if it wasn't CH in last rotation period
            if rounds_since_ch >= rotation_period or node.last_ch_round < 0:
                # Calculate threshold
                r_mod = self.current_round % rotation_period
                threshold = self.p / (1 - self.p * r_mod) if r_mod != 0 else self.p

                # Add energy-based adjustment (enhancement to original LEACH)
                energy_factor = node.energy / node.initial_energy
                adjusted_threshold = threshold * energy_factor

                # Random selection based on threshold
                if random.random() < adjusted_threshold:
                    node.set_cluster_head(True)
                    self.cluster_heads.append(node)
                    self.clusters[node.id] = []
                else:
                    node.set_cluster_head(False)
            else:
                node.set_cluster_head(False)

    def _force_cluster_head_election(self):
        """
        Force at least one cluster head election if none were elected.
        Selects the node with highest residual energy.
        """
        alive_nodes = [node for node in self.network.nodes if node.is_alive()]

        if not alive_nodes:
            return

        # Select node with maximum energy
        best_node = max(alive_nodes, key=lambda n: n.energy)
        best_node.set_cluster_head(True)
        self.cluster_heads.append(best_node)
        self.clusters[best_node.id] = []

    def _form_clusters(self):
        """
        Form clusters by having non-CH nodes join nearest CH.

        Each non-CH node:
        1. Receives advertisements from all CHs
        2. Selects CH with minimum distance (or RSSI)
        3. Sends join request to selected CH
        """
        if not self.cluster_heads:
            return

        # Non-CH nodes join nearest cluster head
        for node in self.network.nodes:
            if node.is_alive() and not node.is_cluster_head:
                # Find nearest cluster head
                nearest_ch = min(
                    self.cluster_heads,
                    key=lambda ch: node.distance_to(ch)
                )

                # Join cluster
                node.join_cluster(nearest_ch)
                self.clusters[nearest_ch.id].append(node)

                # Energy cost for receiving CH advertisement and sending join request
                node.receive()  # Receive CH advertisement
                node.transmit(nearest_ch)  # Send join request

                # CH receives join request
                nearest_ch.receive()

    def steady_state_phase(self):
        """
        Steady-state phase: Data collection and transmission to base station.

        Steps:
        1. Cluster members sense and transmit data to CH
        2. CH aggregates data
        3. CH transmits aggregated data to base station

        Returns:
            Dictionary with phase statistics
        """
        packets_to_bs = 0
        energy_start = sum(node.energy for node in self.network.nodes)

        # Process each cluster
        for ch in self.cluster_heads:
            if not ch.is_alive():
                continue

            cluster_members = self.clusters.get(ch.id, [])
            alive_members = [n for n in cluster_members if n.is_alive()]

            # Step 1: Members send data to CH
            for member in alive_members:
                member.sense()  # Sense data
                member.transmit(ch)  # Send to CH
                ch.receive()  # CH receives

            # Step 2: CH aggregates data
            if alive_members:
                ch.aggregate_data(len(alive_members))

            # Step 3: CH sends aggregated data to base station
            if ch.transmit(self.network.base_station):
                packets_to_bs += 1

        # Update statistics
        self.total_packets_to_bs += packets_to_bs

        energy_end = sum(node.energy for node in self.network.nodes)
        energy_consumed = energy_start - energy_end
        self.total_energy_consumed += energy_consumed

        # Collect statistics
        alive_nodes = [n for n in self.network.nodes if n.is_alive()]
        stats = {
            'round': self.current_round,
            'num_cluster_heads': len(self.cluster_heads),
            'packets_to_bs': packets_to_bs,
            'energy_consumed': energy_consumed,
            'alive_nodes': len(alive_nodes),
            'total_energy': sum(n.energy for n in self.network.nodes),
            'avg_energy': sum(n.energy for n in self.network.nodes) / len(self.network.nodes) if self.network.nodes else 0,
        }

        return stats

    def get_clustering_info(self):
        """
        Get current clustering information.

        Returns:
            Dictionary with clustering details
        """
        cluster_sizes = {ch.id: len(self.clusters[ch.id]) for ch in self.cluster_heads}

        return {
            'round': self.current_round,
            'num_clusters': len(self.cluster_heads),
            'cluster_heads': [ch.id for ch in self.cluster_heads],
            'cluster_sizes': cluster_sizes,
            'avg_cluster_size': sum(cluster_sizes.values()) / len(cluster_sizes) if cluster_sizes else 0,
        }

    def get_statistics(self):
        """
        Get protocol statistics.

        Returns:
            Dictionary with comprehensive statistics
        """
        alive_nodes = [n for n in self.network.nodes if n.is_alive()]
        dead_nodes = [n for n in self.network.nodes if n.is_dead()]

        return {
            'total_rounds': self.current_round,
            'alive_nodes': len(alive_nodes),
            'dead_nodes': len(dead_nodes),
            'total_packets_to_bs': self.total_packets_to_bs,
            'total_energy_consumed': self.total_energy_consumed,
            'avg_packets_per_round': self.total_packets_to_bs / self.current_round if self.current_round > 0 else 0,
            'current_cluster_heads': len(self.cluster_heads),
        }

    def print_round_info(self):
        """Print information about current round"""
        clustering_info = self.get_clustering_info()
        stats = self.get_statistics()

        print(f"\n=== Round {self.current_round} ===")
        print(f"Cluster Heads: {clustering_info['num_clusters']}")
        print(f"Average Cluster Size: {clustering_info['avg_cluster_size']:.2f}")
        print(f"Alive Nodes: {stats['alive_nodes']}/{len(self.network.nodes)}")
        print(f"Packets to BS: {stats['total_packets_to_bs']}")
        print(f"Total Energy Consumed: {stats['total_energy_consumed']:.6f} J")
