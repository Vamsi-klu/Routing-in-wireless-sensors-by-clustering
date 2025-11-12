"""
Advanced Performance Analysis Example

Demonstrates advanced features including:
- Parameter sensitivity analysis
- Comparison of different configurations
- Statistical analysis and reporting
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import matplotlib.pyplot as plt
from src.network import WirelessSensorNetwork
from src.leach import LEACH
from visualization.metrics import PerformanceAnalyzer
from src.utils import save_simulation_results, export_to_csv


def parameter_sensitivity_analysis():
    """Analyze sensitivity to cluster head probability"""

    print("="*70)
    print("PARAMETER SENSITIVITY ANALYSIS")
    print("="*70)

    # Test different CH probabilities
    ch_probabilities = [0.02, 0.05, 0.08, 0.10, 0.15, 0.20]
    results = {}

    for p in ch_probabilities:
        print(f"\nTesting CH probability: {p*100}%")

        # Create network
        network = WirelessSensorNetwork(
            num_nodes=100,
            area_size=(100, 100),
            base_station=(50, 150),
            initial_energy=0.5,
            deployment='random'
        )

        # Run LEACH
        leach = LEACH(network, cluster_head_probability=p)

        # Run simulation
        for round_num in range(1, 2000):
            leach.run_round()
            network.update_lifetime_stats(round_num)

            if network.is_dead():
                break

        # Collect results
        analyzer = PerformanceAnalyzer(leach.rounds_history)
        report = analyzer.get_comprehensive_report()

        results[f"p={p}"] = {
            'probability': p,
            'fnd': report['lifetime']['first_node_death'],
            'hnd': report['lifetime']['half_nodes_death'],
            'total_packets': report['throughput']['total_packets_to_bs'],
            'avg_cluster_heads': report['clustering']['avg_cluster_heads'],
            'total_energy': report['energy']['total_energy_consumed'],
        }

        print(f"   FND: {report['lifetime']['first_node_death']}")
        print(f"   HND: {report['lifetime']['half_nodes_death']}")
        print(f"   Total packets: {report['throughput']['total_packets_to_bs']}")

    # Plot results
    print("\nGenerating comparison plots...")
    plot_sensitivity_results(results)

    # Export to CSV
    csv_data = []
    for config, data in results.items():
        csv_data.append(data)

    export_to_csv(csv_data, 'sensitivity_analysis.csv')
    print("\nResults exported to sensitivity_analysis.csv")

    return results


def plot_sensitivity_results(results):
    """Plot sensitivity analysis results"""

    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 10))

    probabilities = [data['probability'] for data in results.values()]
    fnds = [data['fnd'] for data in results.values()]
    hnds = [data['hnd'] for data in results.values()]
    packets = [data['total_packets'] for data in results.values()]
    avg_chs = [data['avg_cluster_heads'] for data in results.values()]

    # FND vs CH probability
    ax1.plot(probabilities, fnds, 'bo-', linewidth=2, markersize=8)
    ax1.set_xlabel('Cluster Head Probability', fontsize=12)
    ax1.set_ylabel('First Node Death (Round)', fontsize=12)
    ax1.set_title('Network Lifetime vs CH Probability', fontsize=13, fontweight='bold')
    ax1.grid(True, alpha=0.3)

    # HND vs CH probability
    ax2.plot(probabilities, hnds, 'ro-', linewidth=2, markersize=8)
    ax2.set_xlabel('Cluster Head Probability', fontsize=12)
    ax2.set_ylabel('Half Nodes Death (Round)', fontsize=12)
    ax2.set_title('Half Nodes Death vs CH Probability', fontsize=13, fontweight='bold')
    ax2.grid(True, alpha=0.3)

    # Total packets vs CH probability
    ax3.plot(probabilities, packets, 'go-', linewidth=2, markersize=8)
    ax3.set_xlabel('Cluster Head Probability', fontsize=12)
    ax3.set_ylabel('Total Packets to BS', fontsize=12)
    ax3.set_title('Throughput vs CH Probability', fontsize=13, fontweight='bold')
    ax3.grid(True, alpha=0.3)

    # Average CHs vs CH probability
    ax4.plot(probabilities, avg_chs, 'mo-', linewidth=2, markersize=8)
    ax4.set_xlabel('Cluster Head Probability', fontsize=12)
    ax4.set_ylabel('Average Cluster Heads', fontsize=12)
    ax4.set_title('Average CHs vs CH Probability', fontsize=13, fontweight='bold')
    ax4.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('sensitivity_analysis.png', dpi=300, bbox_inches='tight')
    print("Sensitivity analysis plot saved to sensitivity_analysis.png")
    plt.show()


def deployment_comparison():
    """Compare different node deployment strategies"""

    print("\n" + "="*70)
    print("DEPLOYMENT STRATEGY COMPARISON")
    print("="*70)

    deployments = ['random', 'grid', 'cluster']
    results = {}

    for deployment in deployments:
        print(f"\nTesting deployment: {deployment}")

        # Create network
        network = WirelessSensorNetwork(
            num_nodes=100,
            area_size=(100, 100),
            base_station=(50, 150),
            initial_energy=0.5,
            deployment=deployment
        )

        # Run LEACH
        leach = LEACH(network, cluster_head_probability=0.05)

        # Run simulation
        for round_num in range(1, 2000):
            leach.run_round()
            network.update_lifetime_stats(round_num)

            if network.is_dead():
                break

        # Analyze results
        analyzer = PerformanceAnalyzer(leach.rounds_history)
        report = analyzer.get_comprehensive_report()

        results[deployment] = leach.rounds_history

        print(f"   FND: {report['lifetime']['first_node_death']}")
        print(f"   HND: {report['lifetime']['half_nodes_death']}")
        print(f"   Total packets: {report['throughput']['total_packets_to_bs']}")

    # Plot comparison
    print("\nGenerating comparison plots...")
    plot_deployment_comparison(results)


def plot_deployment_comparison(results):
    """Plot deployment comparison"""

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    for deployment, rounds_history in results.items():
        rounds = [stats['round'] for stats in rounds_history]
        alive_nodes = [stats.get('alive_nodes', 0) for stats in rounds_history]
        cumulative_packets = np.cumsum([stats.get('packets_to_bs', 0) for stats in rounds_history])

        ax1.plot(rounds, alive_nodes, linewidth=2, label=deployment.capitalize(), alpha=0.8)
        ax2.plot(rounds, cumulative_packets, linewidth=2, label=deployment.capitalize(), alpha=0.8)

    ax1.set_xlabel('Round', fontsize=12)
    ax1.set_ylabel('Alive Nodes', fontsize=12)
    ax1.set_title('Network Lifetime by Deployment', fontsize=13, fontweight='bold')
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    ax2.set_xlabel('Round', fontsize=12)
    ax2.set_ylabel('Cumulative Packets to BS', fontsize=12)
    ax2.set_title('Throughput by Deployment', fontsize=13, fontweight='bold')
    ax2.legend()
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('deployment_comparison.png', dpi=300, bbox_inches='tight')
    print("Deployment comparison plot saved to deployment_comparison.png")
    plt.show()


def multiple_run_analysis(num_runs=10):
    """Run multiple simulations and compute statistical metrics"""

    print("\n" + "="*70)
    print(f"MULTIPLE RUN ANALYSIS ({num_runs} runs)")
    print("="*70)

    fnds = []
    hnds = []
    total_packets_list = []

    for run in range(1, num_runs + 1):
        print(f"\nRun {run}/{num_runs}...")

        # Create network with random seed
        network = WirelessSensorNetwork(
            num_nodes=100,
            area_size=(100, 100),
            base_station=(50, 150),
            initial_energy=0.5,
            deployment='random'
        )

        # Run LEACH
        leach = LEACH(network, cluster_head_probability=0.05)

        for round_num in range(1, 2000):
            leach.run_round()
            network.update_lifetime_stats(round_num)

            if network.is_dead():
                break

        # Collect metrics
        analyzer = PerformanceAnalyzer(leach.rounds_history)
        report = analyzer.get_comprehensive_report()

        fnds.append(report['lifetime']['first_node_death'])
        hnds.append(report['lifetime']['half_nodes_death'])
        total_packets_list.append(report['throughput']['total_packets_to_bs'])

    # Statistical analysis
    print("\n" + "="*70)
    print("STATISTICAL RESULTS")
    print("="*70)

    print(f"\nFirst Node Death (FND):")
    print(f"   Mean: {np.mean(fnds):.2f} rounds")
    print(f"   Std Dev: {np.std(fnds):.2f}")
    print(f"   Min: {np.min(fnds)}, Max: {np.max(fnds)}")

    print(f"\nHalf Nodes Death (HND):")
    print(f"   Mean: {np.mean(hnds):.2f} rounds")
    print(f"   Std Dev: {np.std(hnds):.2f}")
    print(f"   Min: {np.min(hnds)}, Max: {np.max(hnds)}")

    print(f"\nTotal Packets:")
    print(f"   Mean: {np.mean(total_packets_list):.2f}")
    print(f"   Std Dev: {np.std(total_packets_list):.2f}")
    print(f"   Min: {np.min(total_packets_list)}, Max: {np.max(total_packets_list)}")

    # Box plots
    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(15, 5))

    ax1.boxplot(fnds)
    ax1.set_ylabel('Rounds', fontsize=12)
    ax1.set_title('First Node Death', fontsize=13, fontweight='bold')
    ax1.grid(True, alpha=0.3, axis='y')

    ax2.boxplot(hnds)
    ax2.set_ylabel('Rounds', fontsize=12)
    ax2.set_title('Half Nodes Death', fontsize=13, fontweight='bold')
    ax2.grid(True, alpha=0.3, axis='y')

    ax3.boxplot(total_packets_list)
    ax3.set_ylabel('Packets', fontsize=12)
    ax3.set_title('Total Packets to BS', fontsize=13, fontweight='bold')
    ax3.grid(True, alpha=0.3, axis='y')

    plt.tight_layout()
    plt.savefig('statistical_analysis.png', dpi=300, bbox_inches='tight')
    print("\nStatistical analysis plot saved to statistical_analysis.png")
    plt.show()


if __name__ == "__main__":
    # Run analyses
    print("\nSelect analysis to run:")
    print("1. Parameter Sensitivity Analysis")
    print("2. Deployment Strategy Comparison")
    print("3. Multiple Run Statistical Analysis")
    print("4. Run All")

    choice = input("\nEnter choice (1-4): ").strip()

    if choice == '1':
        parameter_sensitivity_analysis()
    elif choice == '2':
        deployment_comparison()
    elif choice == '3':
        multiple_run_analysis()
    elif choice == '4':
        parameter_sensitivity_analysis()
        deployment_comparison()
        multiple_run_analysis()
    else:
        print("Invalid choice. Running all analyses...")
        parameter_sensitivity_analysis()
        deployment_comparison()
        multiple_run_analysis()

    print("\n" + "="*70)
    print("ANALYSIS COMPLETE")
    print("="*70)
