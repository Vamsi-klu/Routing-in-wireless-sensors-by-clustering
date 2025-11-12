"""
Visualization tools for Wireless Sensor Networks

Provides plotting and visualization capabilities for network topology,
energy distribution, clustering, and performance metrics.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.animation import FuncAnimation
import numpy as np


class NetworkVisualizer:
    """Visualizer for WSN topology and statistics"""

    def __init__(self, network):
        """
        Initialize visualizer.

        Args:
            network: WirelessSensorNetwork instance
        """
        self.network = network

    def plot_topology(self, show_clusters=False, show_connections=False,
                     save_path=None, title="WSN Topology"):
        """
        Plot network topology showing nodes and base station.

        Args:
            show_clusters: Show cluster membership if True
            show_connections: Show communication links if True
            save_path: Path to save figure (optional)
            title: Plot title
        """
        fig, ax = plt.subplots(figsize=(12, 10))

        # Plot alive nodes
        alive_nodes = self.network.get_alive_nodes()
        dead_nodes = self.network.get_dead_nodes()

        if show_clusters:
            # Color nodes by cluster
            cluster_colors = {}
            color_idx = 0
            colors = plt.cm.tab20(np.linspace(0, 1, 20))

            for node in alive_nodes:
                if node.is_cluster_head:
                    ch_id = node.id
                    cluster_colors[ch_id] = colors[color_idx % 20]
                    color_idx += 1

            # Plot cluster members
            for node in alive_nodes:
                if not node.is_cluster_head and node.cluster_head:
                    ch_id = node.cluster_head.id
                    color = cluster_colors.get(ch_id, 'lightblue')
                    ax.scatter(node.x, node.y, c=[color], s=50, alpha=0.6,
                             edgecolors='black', linewidth=0.5)

                    if show_connections:
                        ax.plot([node.x, node.cluster_head.x],
                               [node.y, node.cluster_head.y],
                               'gray', alpha=0.3, linewidth=0.5)

            # Plot cluster heads
            ch_nodes = [n for n in alive_nodes if n.is_cluster_head]
            if ch_nodes:
                ch_x = [n.x for n in ch_nodes]
                ch_y = [n.y for n in ch_nodes]
                ch_colors = [cluster_colors.get(n.id, 'red') for n in ch_nodes]
                ax.scatter(ch_x, ch_y, c=ch_colors, s=200, marker='^',
                         edgecolors='black', linewidth=2, label='Cluster Heads',
                         alpha=0.9)

                if show_connections:
                    # Show CH to BS connections
                    for ch in ch_nodes:
                        ax.plot([ch.x, self.network.base_station[0]],
                               [ch.y, self.network.base_station[1]],
                               'blue', alpha=0.2, linewidth=1)

            # Plot regular alive nodes without cluster
            regular_nodes = [n for n in alive_nodes if not n.is_cluster_head and not n.cluster_head]
            if regular_nodes:
                reg_x = [n.x for n in regular_nodes]
                reg_y = [n.y for n in regular_nodes]
                ax.scatter(reg_x, reg_y, c='lightblue', s=50, alpha=0.6,
                         edgecolors='black', linewidth=0.5, label='Nodes')
        else:
            # Simple plot by energy level
            if alive_nodes:
                for node in alive_nodes:
                    energy_pct = node.get_energy_percentage()
                    color = plt.cm.RdYlGn(energy_pct / 100)
                    size = 100 if node.is_cluster_head else 50
                    marker = '^' if node.is_cluster_head else 'o'
                    ax.scatter(node.x, node.y, c=[color], s=size, marker=marker,
                             edgecolors='black', linewidth=1, alpha=0.8)

        # Plot dead nodes
        if dead_nodes:
            dead_x = [n.x for n in dead_nodes]
            dead_y = [n.y for n in dead_nodes]
            ax.scatter(dead_x, dead_y, c='black', s=30, marker='x',
                     label='Dead Nodes', alpha=0.5)

        # Plot base station
        ax.scatter(self.network.base_station[0], self.network.base_station[1],
                  c='gold', s=400, marker='*', edgecolors='black',
                  linewidth=2, label='Base Station', zorder=10)

        # Add deployment area boundary
        rect = patches.Rectangle((0, 0), self.network.area_width,
                                self.network.area_height,
                                linewidth=2, edgecolor='black',
                                facecolor='none', linestyle='--')
        ax.add_patch(rect)

        ax.set_xlim(-10, max(self.network.area_width, self.network.base_station[0]) + 10)
        ax.set_ylim(-10, max(self.network.area_height, self.network.base_station[1]) + 10)
        ax.set_xlabel('X (meters)', fontsize=12)
        ax.set_ylabel('Y (meters)', fontsize=12)
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.legend(loc='upper right')
        ax.grid(True, alpha=0.3)
        ax.set_aspect('equal')

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Topology plot saved to {save_path}")

        plt.show()

    def plot_energy_distribution(self, save_path=None):
        """
        Plot energy distribution across nodes.

        Args:
            save_path: Path to save figure (optional)
        """
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

        # Energy histogram
        alive_nodes = self.network.get_alive_nodes()
        if alive_nodes:
            energies = [node.energy for node in alive_nodes]
            ax1.hist(energies, bins=20, color='skyblue', edgecolor='black', alpha=0.7)
            ax1.axvline(np.mean(energies), color='red', linestyle='--',
                       linewidth=2, label=f'Mean: {np.mean(energies):.4f} J')
            ax1.set_xlabel('Energy (Joules)', fontsize=12)
            ax1.set_ylabel('Number of Nodes', fontsize=12)
            ax1.set_title('Energy Distribution', fontsize=14, fontweight='bold')
            ax1.legend()
            ax1.grid(True, alpha=0.3)

        # Energy percentages
        energy_percentages = [node.get_energy_percentage() for node in self.network.nodes]
        ax2.hist(energy_percentages, bins=20, color='lightgreen',
                edgecolor='black', alpha=0.7)
        ax2.axvline(np.mean(energy_percentages), color='red', linestyle='--',
                   linewidth=2, label=f'Mean: {np.mean(energy_percentages):.1f}%')
        ax2.set_xlabel('Remaining Energy (%)', fontsize=12)
        ax2.set_ylabel('Number of Nodes', fontsize=12)
        ax2.set_title('Energy Percentage Distribution', fontsize=14, fontweight='bold')
        ax2.legend()
        ax2.grid(True, alpha=0.3)

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Energy distribution plot saved to {save_path}")

        plt.show()

    def plot_node_positions_with_energy(self, save_path=None):
        """
        Plot node positions colored by energy level.

        Args:
            save_path: Path to save figure (optional)
        """
        fig, ax = plt.subplots(figsize=(12, 10))

        alive_nodes = self.network.get_alive_nodes()
        dead_nodes = self.network.get_dead_nodes()

        if alive_nodes:
            x = [n.x for n in alive_nodes]
            y = [n.y for n in alive_nodes]
            energies = [n.get_energy_percentage() for n in alive_nodes]

            scatter = ax.scatter(x, y, c=energies, cmap='RdYlGn',
                               s=100, vmin=0, vmax=100,
                               edgecolors='black', linewidth=1)
            cbar = plt.colorbar(scatter, ax=ax)
            cbar.set_label('Remaining Energy (%)', fontsize=12)

        if dead_nodes:
            dead_x = [n.x for n in dead_nodes]
            dead_y = [n.y for n in dead_nodes]
            ax.scatter(dead_x, dead_y, c='black', s=50, marker='x',
                     label='Dead Nodes', alpha=0.7)

        # Base station
        ax.scatter(self.network.base_station[0], self.network.base_station[1],
                  c='gold', s=400, marker='*', edgecolors='black',
                  linewidth=2, label='Base Station', zorder=10)

        ax.set_xlabel('X (meters)', fontsize=12)
        ax.set_ylabel('Y (meters)', fontsize=12)
        ax.set_title('Network Topology - Energy Levels', fontsize=14, fontweight='bold')
        ax.legend()
        ax.grid(True, alpha=0.3)
        ax.set_aspect('equal')

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')

        plt.show()


def plot_protocol_comparison(protocols_data, metric='alive_nodes', save_path=None):
    """
    Compare multiple protocols on a given metric.

    Args:
        protocols_data: Dict {protocol_name: [round_stats_list]}
        metric: Metric to compare
        save_path: Path to save figure (optional)
    """
    fig, ax = plt.subplots(figsize=(12, 6))

    for protocol_name, rounds_stats in protocols_data.items():
        rounds = [stats['round'] for stats in rounds_stats]
        values = [stats[metric] for stats in rounds_stats]
        ax.plot(rounds, values, marker='o', markersize=3,
               linewidth=2, label=protocol_name, alpha=0.8)

    ax.set_xlabel('Round', fontsize=12)
    ax.set_ylabel(metric.replace('_', ' ').title(), fontsize=12)
    ax.set_title(f'Protocol Comparison - {metric.replace("_", " ").title()}',
                fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')

    plt.show()
