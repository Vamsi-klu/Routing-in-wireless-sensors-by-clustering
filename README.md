# Routing in Wireless Sensor Networks by Clustering

A comprehensive implementation of clustering-based routing protocols for Wireless Sensor Networks (WSN), featuring the LEACH (Low Energy Adaptive Clustering Hierarchy) algorithm and advanced energy-efficient routing mechanisms.

## Features

- **LEACH Protocol Implementation**: Complete implementation of the LEACH clustering algorithm
- **Energy Models**: Realistic energy consumption models for transmission, reception, and data aggregation
- **Network Simulation**: Full WSN simulation engine with configurable parameters
- **Cluster Formation**: Dynamic cluster head selection and cluster formation
- **Multi-hop Routing**: Support for both direct and multi-hop communication
- **Visualization**: Real-time network topology and energy visualization
- **Performance Metrics**: Comprehensive analysis including network lifetime, energy consumption, throughput, and latency
- **Extensible Architecture**: Easy to add new clustering algorithms and protocols

## Architecture

```
├── src/
│   ├── node.py              # Sensor node implementation with energy model
│   ├── leach.py             # LEACH clustering algorithm
│   ├── network.py           # Network simulation engine
│   ├── routing.py           # Routing mechanisms
│   ├── energy_model.py      # Energy consumption models
│   └── utils.py             # Utility functions
├── visualization/
│   ├── plotter.py           # Network visualization
│   └── metrics.py           # Performance metrics and analysis
├── examples/
│   ├── basic_simulation.py  # Basic usage example
│   └── advanced_analysis.py # Advanced performance analysis
├── config/
│   └── config.yaml          # Configuration parameters
└── tests/
    └── test_*.py            # Unit tests
```

## Algorithms Implemented

### LEACH (Low Energy Adaptive Clustering Hierarchy)
- **Cluster Head Selection**: Probabilistic selection based on energy and rotation
- **Setup Phase**: Cluster formation and TDMA schedule creation
- **Steady-State Phase**: Data collection, aggregation, and transmission
- **Energy Optimization**: Balanced energy consumption across nodes

## Installation

```bash
pip install -r requirements.txt
```

## Quick Start

```python
from src.network import WirelessSensorNetwork
from src.leach import LEACH

# Create network with 100 nodes in 100x100m area
network = WirelessSensorNetwork(
    num_nodes=100,
    area_size=(100, 100),
    base_station=(50, 150)
)

# Initialize LEACH protocol
leach = LEACH(network, cluster_head_probability=0.1)

# Run simulation for 1000 rounds
for round in range(1000):
    leach.run_round()
    if network.is_dead():
        print(f"Network died at round {round}")
        break

# Visualize results
network.plot_topology()
network.plot_energy_consumption()
network.print_statistics()
```

## Configuration

Edit `config/config.yaml` to customize:
- Network size and topology
- Energy parameters
- Transmission ranges
- Clustering parameters
- Protocol settings

## Performance Metrics

The implementation tracks:
- **Network Lifetime**: First node death (FND), half nodes death (HND), last node death (LND)
- **Energy Efficiency**: Total energy consumption, average residual energy
- **Throughput**: Packets delivered to base station
- **Latency**: End-to-end delay
- **Coverage**: Network coverage over time

## Research Applications

This implementation is suitable for:
- WSN protocol research and development
- Energy efficiency analysis
- Comparative studies of clustering algorithms
- Educational purposes in wireless networking courses
- IoT network simulation

## License

MIT License

## Author

Implemented for WSN routing research and educational purposes.
