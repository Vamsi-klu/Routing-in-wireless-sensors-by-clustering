"""
Basic LEACH Simulation Example

Demonstrates basic usage of the WSN simulation framework with LEACH protocol.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.network import WirelessSensorNetwork
from src.leach import LEACH
from visualization.plotter import NetworkVisualizer
from visualization.metrics import PerformanceAnalyzer


def run_basic_simulation():
    """Run a basic LEACH simulation"""

    print("="*70)
    print("BASIC LEACH SIMULATION")
    print("="*70)

    # Create network
    print("\n1. Creating wireless sensor network...")
    network = WirelessSensorNetwork(
        num_nodes=100,
        area_size=(100, 100),
        base_station=(50, 150),
        initial_energy=0.5,
        deployment='random',
        random_seed=42  # For reproducible results
    )
    print(f"   Created network with {network.num_nodes} nodes")
    print(f"   Deployment area: {network.area_width}x{network.area_height} meters")
    print(f"   Base station at: {network.base_station}")
    print(f"   Random seed: {network.random_seed} (for reproducibility)")

    # Initialize LEACH
    print("\n2. Initializing LEACH protocol...")
    leach = LEACH(
        network=network,
        cluster_head_probability=0.05,
        round_time=20
    )
    print(f"   Cluster head probability: {leach.p*100}%")

    # Run simulation
    print("\n3. Running simulation...")
    max_rounds = 1000
    print_interval = 100

    for round_num in range(1, max_rounds + 1):
        # Run one round
        stats = leach.run_round()

        # Update network lifetime stats
        network.update_lifetime_stats(round_num)

        # Print progress
        if round_num % print_interval == 0:
            print(f"\n   Round {round_num}:")
            print(f"   - Alive nodes: {stats['alive_nodes']}/{network.num_nodes}")
            print(f"   - Cluster heads: {stats['num_cluster_heads']}")
            print(f"   - Packets to BS: {stats['packets_to_bs']}")
            print(f"   - Avg energy: {stats['avg_energy']:.4f} J")

        # Stop if network is dead
        if network.is_dead():
            print(f"\n   Network died at round {round_num}")
            break

    # Print final statistics
    print("\n4. Simulation complete!")
    print("\n" + "="*70)
    print("FINAL STATISTICS")
    print("="*70)
    network.print_statistics()

    # Performance analysis
    print("\n5. Performance analysis...")
    analyzer = PerformanceAnalyzer(leach.rounds_history)
    analyzer.print_report()

    # Visualization
    print("\n6. Generating visualizations...")
    visualizer = NetworkVisualizer(network)

    print("   - Plotting network topology...")
    visualizer.plot_topology(
        show_clusters=True,
        show_connections=True,
        title=f"Final Network Topology (Round {leach.current_round})"
    )

    print("   - Plotting energy distribution...")
    visualizer.plot_energy_distribution()

    print("   - Plotting performance metrics...")
    analyzer.plot_metrics_over_time()

    print("\n" + "="*70)
    print("SIMULATION COMPLETE")
    print("="*70)


if __name__ == "__main__":
    run_basic_simulation()
