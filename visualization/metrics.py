"""
Performance Metrics and Analysis Tools

Provides comprehensive performance evaluation metrics for WSN protocols
including network lifetime, energy efficiency, throughput, and latency.
"""

import matplotlib.pyplot as plt
import numpy as np
from src.utils import moving_average


class PerformanceAnalyzer:
    """Analyzer for WSN protocol performance metrics"""

    def __init__(self, rounds_history):
        """
        Initialize analyzer with simulation history.

        Args:
            rounds_history: List of round statistics dictionaries
        """
        self.rounds_history = rounds_history

    def get_network_lifetime_metrics(self):
        """
        Calculate network lifetime metrics.

        Returns:
            Dictionary with FND, HND, LND, and stability period
        """
        first_node_death = None
        half_nodes_death = None
        last_node_death = None

        total_nodes = None

        for i, stats in enumerate(self.rounds_history):
            if total_nodes is None and 'alive_nodes' in stats:
                # Infer total nodes from first round
                total_nodes = stats['alive_nodes']

            alive = stats.get('alive_nodes', 0)

            if first_node_death is None and alive < total_nodes:
                first_node_death = stats['round']

            if half_nodes_death is None and alive <= total_nodes / 2:
                half_nodes_death = stats['round']

            if last_node_death is None and alive == 0:
                last_node_death = stats['round']
                break

        stability_period = first_node_death if first_node_death else len(self.rounds_history)

        return {
            'first_node_death': first_node_death,
            'half_nodes_death': half_nodes_death,
            'last_node_death': last_node_death,
            'stability_period': stability_period,
            'total_rounds': len(self.rounds_history)
        }

    def get_energy_metrics(self):
        """
        Calculate energy consumption metrics.

        Returns:
            Dictionary with energy statistics
        """
        total_energy_consumed = sum(stats.get('energy_consumed', 0)
                                   for stats in self.rounds_history)

        avg_energy_per_round = (total_energy_consumed / len(self.rounds_history)
                               if self.rounds_history else 0)

        # Energy depletion rate
        if len(self.rounds_history) > 1:
            energy_start = self.rounds_history[0].get('total_energy', 0)
            energy_end = self.rounds_history[-1].get('total_energy', 0)
            depletion_rate = (energy_start - energy_end) / len(self.rounds_history)
        else:
            depletion_rate = 0

        return {
            'total_energy_consumed': total_energy_consumed,
            'avg_energy_per_round': avg_energy_per_round,
            'energy_depletion_rate': depletion_rate,
        }

    def get_throughput_metrics(self):
        """
        Calculate throughput metrics.

        Returns:
            Dictionary with throughput statistics
        """
        total_packets = sum(stats.get('packets_to_bs', 0)
                          for stats in self.rounds_history)

        avg_packets_per_round = (total_packets / len(self.rounds_history)
                                if self.rounds_history else 0)

        # Calculate throughput variance
        packets_per_round = [stats.get('packets_to_bs', 0)
                            for stats in self.rounds_history]
        throughput_variance = np.var(packets_per_round) if packets_per_round else 0

        return {
            'total_packets_to_bs': total_packets,
            'avg_packets_per_round': avg_packets_per_round,
            'throughput_variance': throughput_variance,
        }

    def get_clustering_metrics(self):
        """
        Calculate clustering-related metrics.

        Returns:
            Dictionary with clustering statistics
        """
        cluster_head_counts = [stats.get('num_cluster_heads', 0)
                              for stats in self.rounds_history]

        avg_cluster_heads = np.mean(cluster_head_counts) if cluster_head_counts else 0
        std_cluster_heads = np.std(cluster_head_counts) if cluster_head_counts else 0

        return {
            'avg_cluster_heads': avg_cluster_heads,
            'std_cluster_heads': std_cluster_heads,
            'min_cluster_heads': min(cluster_head_counts) if cluster_head_counts else 0,
            'max_cluster_heads': max(cluster_head_counts) if cluster_head_counts else 0,
        }

    def get_comprehensive_report(self):
        """
        Generate comprehensive performance report.

        Returns:
            Dictionary with all metrics
        """
        return {
            'lifetime': self.get_network_lifetime_metrics(),
            'energy': self.get_energy_metrics(),
            'throughput': self.get_throughput_metrics(),
            'clustering': self.get_clustering_metrics(),
        }

    def print_report(self):
        """Print comprehensive performance report"""
        report = self.get_comprehensive_report()

        print("\n" + "="*70)
        print("PERFORMANCE ANALYSIS REPORT")
        print("="*70)

        print("\n--- NETWORK LIFETIME ---")
        lifetime = report['lifetime']
        print(f"First Node Death (FND): Round {lifetime['first_node_death']}")
        print(f"Half Nodes Death (HND): Round {lifetime['half_nodes_death']}")
        print(f"Last Node Death (LND): Round {lifetime['last_node_death']}")
        print(f"Stability Period: {lifetime['stability_period']} rounds")
        print(f"Total Rounds: {lifetime['total_rounds']}")

        print("\n--- ENERGY EFFICIENCY ---")
        energy = report['energy']
        print(f"Total Energy Consumed: {energy['total_energy_consumed']:.6f} J")
        print(f"Average Energy per Round: {energy['avg_energy_per_round']:.6f} J")
        print(f"Energy Depletion Rate: {energy['energy_depletion_rate']:.6f} J/round")

        print("\n--- THROUGHPUT ---")
        throughput = report['throughput']
        print(f"Total Packets to BS: {throughput['total_packets_to_bs']}")
        print(f"Average Packets per Round: {throughput['avg_packets_per_round']:.2f}")
        print(f"Throughput Variance: {throughput['throughput_variance']:.2f}")

        print("\n--- CLUSTERING ---")
        clustering = report['clustering']
        print(f"Average Cluster Heads: {clustering['avg_cluster_heads']:.2f}")
        print(f"Std Dev Cluster Heads: {clustering['std_cluster_heads']:.2f}")
        print(f"Min Cluster Heads: {clustering['min_cluster_heads']}")
        print(f"Max Cluster Heads: {clustering['max_cluster_heads']}")

        print("="*70 + "\n")

    def plot_metrics_over_time(self, save_path=None):
        """
        Plot key metrics over time.

        Args:
            save_path: Path to save figure (optional)
        """
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))

        rounds = [stats['round'] for stats in self.rounds_history]

        # 1. Alive nodes over time
        alive_nodes = [stats.get('alive_nodes', 0) for stats in self.rounds_history]
        ax1.plot(rounds, alive_nodes, 'b-', linewidth=2)
        ax1.set_xlabel('Round', fontsize=12)
        ax1.set_ylabel('Number of Alive Nodes', fontsize=12)
        ax1.set_title('Network Lifetime', fontsize=14, fontweight='bold')
        ax1.grid(True, alpha=0.3)

        # Mark FND, HND
        lifetime = self.get_network_lifetime_metrics()
        if lifetime['first_node_death']:
            ax1.axvline(lifetime['first_node_death'], color='orange',
                       linestyle='--', label='FND', linewidth=2)
        if lifetime['half_nodes_death']:
            ax1.axvline(lifetime['half_nodes_death'], color='red',
                       linestyle='--', label='HND', linewidth=2)
        ax1.legend()

        # 2. Energy consumption over time
        energy_consumed = [stats.get('energy_consumed', 0) for stats in self.rounds_history]
        cumulative_energy = np.cumsum(energy_consumed)
        ax2.plot(rounds, cumulative_energy, 'r-', linewidth=2)
        ax2.set_xlabel('Round', fontsize=12)
        ax2.set_ylabel('Cumulative Energy Consumed (J)', fontsize=12)
        ax2.set_title('Energy Consumption', fontsize=14, fontweight='bold')
        ax2.grid(True, alpha=0.3)

        # 3. Throughput over time
        packets = [stats.get('packets_to_bs', 0) for stats in self.rounds_history]
        cumulative_packets = np.cumsum(packets)
        ax3.plot(rounds, cumulative_packets, 'g-', linewidth=2)
        ax3.set_xlabel('Round', fontsize=12)
        ax3.set_ylabel('Cumulative Packets to BS', fontsize=12)
        ax3.set_title('Throughput', fontsize=14, fontweight='bold')
        ax3.grid(True, alpha=0.3)

        # 4. Cluster heads over time
        cluster_heads = [stats.get('num_cluster_heads', 0) for stats in self.rounds_history]
        ax4.plot(rounds, cluster_heads, 'm-', linewidth=2, alpha=0.5)

        # Add moving average
        if len(cluster_heads) >= 10:
            ma = moving_average(cluster_heads, window_size=10)
            ax4.plot(rounds, ma, 'purple', linewidth=3, label='Moving Avg (10)')
            ax4.legend()

        ax4.set_xlabel('Round', fontsize=12)
        ax4.set_ylabel('Number of Cluster Heads', fontsize=12)
        ax4.set_title('Cluster Head Distribution', fontsize=14, fontweight='bold')
        ax4.grid(True, alpha=0.3)

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Metrics plot saved to {save_path}")

        plt.show()

    def plot_energy_efficiency(self, save_path=None):
        """
        Plot energy efficiency metrics.

        Args:
            save_path: Path to save figure (optional)
        """
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

        rounds = [stats['round'] for stats in self.rounds_history]

        # Energy per round
        energy_per_round = [stats.get('energy_consumed', 0) for stats in self.rounds_history]
        ax1.bar(rounds, energy_per_round, color='coral', alpha=0.7)
        ax1.set_xlabel('Round', fontsize=12)
        ax1.set_ylabel('Energy Consumed (J)', fontsize=12)
        ax1.set_title('Energy Consumption per Round', fontsize=14, fontweight='bold')
        ax1.grid(True, alpha=0.3, axis='y')

        # Packets vs Energy efficiency
        packets = [stats.get('packets_to_bs', 0) for stats in self.rounds_history]
        energy = [stats.get('energy_consumed', 0) for stats in self.rounds_history]

        efficiency = []
        for p, e in zip(packets, energy):
            if e > 0:
                efficiency.append(p / e)
            else:
                efficiency.append(0)

        ax2.plot(rounds, efficiency, 'darkgreen', linewidth=2)
        ax2.set_xlabel('Round', fontsize=12)
        ax2.set_ylabel('Packets per Joule', fontsize=12)
        ax2.set_title('Energy Efficiency', fontsize=14, fontweight='bold')
        ax2.grid(True, alpha=0.3)

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')

        plt.show()
