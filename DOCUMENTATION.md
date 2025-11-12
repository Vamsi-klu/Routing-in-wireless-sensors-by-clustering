# Routing in Wireless Sensor Networks - Technical Documentation

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Core Components](#core-components)
4. [LEACH Protocol](#leach-protocol)
5. [Energy Model](#energy-model)
6. [Routing Mechanisms](#routing-mechanisms)
7. [Performance Metrics](#performance-metrics)
8. [Usage Guide](#usage-guide)
9. [Configuration](#configuration)
10. [Extending the Framework](#extending-the-framework)

---

## Overview

This project implements a comprehensive simulation framework for Wireless Sensor Networks (WSN) with a focus on clustering-based routing protocols. The primary implementation features the LEACH (Low Energy Adaptive Clustering Hierarchy) protocol, which is a seminal hierarchical routing protocol for energy-efficient communication in WSNs.

### Key Features

- **Energy-Aware Design**: Realistic first-order radio energy model
- **Hierarchical Clustering**: LEACH protocol with probabilistic cluster head selection
- **Multiple Routing Strategies**: Direct, multi-hop, cluster-based, and adaptive routing
- **Comprehensive Analysis**: Network lifetime, throughput, energy efficiency metrics
- **Rich Visualization**: Network topology, energy distribution, performance plots
- **Extensible Architecture**: Easy to add new protocols and algorithms

---

## Architecture

### Project Structure

```
Routing-in-wireless-sensors-by-clustering/
├── src/                          # Core implementation
│   ├── __init__.py
│   ├── node.py                   # Sensor node class
│   ├── network.py                # Network simulation engine
│   ├── energy_model.py           # Energy consumption model
│   ├── leach.py                  # LEACH protocol
│   ├── routing.py                # Routing mechanisms
│   └── utils.py                  # Utility functions
├── visualization/                # Visualization and analysis
│   ├── __init__.py
│   ├── plotter.py                # Network visualization
│   └── metrics.py                # Performance metrics
├── examples/                     # Example usage
│   ├── basic_simulation.py       # Basic LEACH simulation
│   └── advanced_analysis.py      # Advanced analysis
├── config/                       # Configuration files
│   └── config.yaml               # Simulation parameters
├── tests/                        # Unit tests
│   └── test_basic.py
├── requirements.txt              # Dependencies
├── README.md                     # Quick start guide
└── DOCUMENTATION.md              # This file
```

### Design Patterns

- **Object-Oriented Design**: Each component (node, network, protocol) is a class
- **Separation of Concerns**: Energy model, routing, and visualization are decoupled
- **Strategy Pattern**: Multiple routing strategies can be swapped
- **Observer Pattern**: Network statistics are collected through observers

---

## Core Components

### 1. SensorNode (src/node.py)

Represents an individual sensor node in the network.

**Key Attributes:**
- `id`: Unique identifier
- `x, y`: Physical coordinates
- `energy`: Current remaining energy
- `node_type`: Role (NORMAL, CLUSTER_HEAD, BASE_STATION)
- `state`: Operational state (ACTIVE, SLEEP, DEAD)

**Key Methods:**
```python
node.transmit(destination)      # Transmit data
node.receive()                  # Receive data
node.sense()                    # Perform sensing
node.aggregate_data(n)          # Aggregate n packets
node.distance_to(other)         # Calculate distance
```

### 2. WirelessSensorNetwork (src/network.py)

Manages the overall network topology and provides network-level operations.

**Key Features:**
- **Node Deployment**: Random, grid, or clustered deployment
- **Network Statistics**: Alive/dead nodes, energy distribution
- **Lifetime Tracking**: First/Half/Last node death metrics

**Example:**
```python
network = WirelessSensorNetwork(
    num_nodes=100,
    area_size=(100, 100),
    base_station=(50, 150),
    initial_energy=0.5,
    deployment='random'
)
```

### 3. EnergyModel (src/energy_model.py)

Implements the first-order radio energy model used in WSN research.

**Energy Equations:**

**Transmission:**
```
E_tx = E_elec × k + E_amp × k × d^n
```
where:
- k = number of bits
- d = distance
- n = 2 (free space) or 4 (multi-path)

**Reception:**
```
E_rx = E_elec × k
```

**Data Aggregation:**
```
E_DA = E_DA × k × num_packets
```

---

## LEACH Protocol

### Overview

LEACH (Low Energy Adaptive Clustering Hierarchy) is a clustering-based protocol that uses randomized rotation of cluster heads to evenly distribute energy load among sensor nodes.

### Protocol Phases

#### 1. Setup Phase

**Cluster Head Election:**
- Each node decides whether to become a cluster head based on a threshold function
- Threshold T(n):
  ```
  T(n) = p / (1 - p × (r mod (1/p)))  if n ∈ G
       = 0                             otherwise
  ```
  where:
  - p = desired percentage of cluster heads
  - r = current round
  - G = set of nodes that haven't been CH in last 1/p rounds

**Cluster Formation:**
- Elected CHs broadcast advertisement messages
- Non-CH nodes select nearest CH based on received signal strength
- Nodes send join request to selected CH
- CHs create TDMA schedules for their clusters

#### 2. Steady-State Phase

**Data Collection:**
- Cluster members sense data according to TDMA schedule
- Members transmit data to their cluster head

**Data Aggregation:**
- Cluster heads receive data from all members
- CHs perform data aggregation/fusion

**Data Transmission:**
- CHs transmit aggregated data to base station

### Energy Optimization

LEACH achieves energy efficiency through:
- **Load Distribution**: Rotating CH role distributes energy consumption
- **Data Aggregation**: Reduces number of transmissions to BS
- **Cluster-based Communication**: Short-range intra-cluster, long-range inter-cluster
- **TDMA Scheduling**: Prevents collisions, allows sleep states

### Implementation Details

```python
leach = LEACH(
    network=network,
    cluster_head_probability=0.05,  # 5% CHs
    round_time=20                   # 20 seconds per round
)

# Run simulation
for round in range(1000):
    stats = leach.run_round()
    if network.is_dead():
        break
```

---

## Energy Model

### Radio Energy Parameters

| Parameter | Symbol | Default Value | Description |
|-----------|--------|---------------|-------------|
| Electronics Energy | E_elec | 50 nJ/bit | Energy to run transmitter/receiver |
| Free Space Amp | E_fs | 10 pJ/bit/m² | Free space amplification |
| Multi-path Amp | E_mp | 0.0013 pJ/bit/m⁴ | Multi-path amplification |
| Data Aggregation | E_DA | 5 nJ/bit | Aggregation energy |
| Crossover Distance | d₀ | 87.7 m | Free space vs multi-path threshold |

### Energy Consumption Examples

**Example 1: Short-distance transmission (d = 10m)**
```python
energy = E_elec × 4000 + E_fs × 4000 × 10²
       = 50×10⁻⁹ × 4000 + 10×10⁻¹² × 4000 × 100
       = 0.0002 + 0.000004
       = 0.000204 J
```

**Example 2: Long-distance transmission (d = 100m)**
```python
energy = E_elec × 4000 + E_mp × 4000 × 100⁴
       = 50×10⁻⁹ × 4000 + 0.0013×10⁻¹² × 4000 × 10⁸
       = 0.0002 + 0.00052
       = 0.00072 J
```

---

## Routing Mechanisms

### 1. Direct Transmission Router

**Description:** All nodes transmit directly to the base station.

**Advantages:**
- Simple, no routing overhead
- Single-hop delivery

**Disadvantages:**
- High energy consumption for distant nodes
- Unbalanced energy depletion

**Use Case:** Small networks, nodes close to BS

### 2. Multi-Hop Router

**Description:** Uses Dijkstra's algorithm to find energy-efficient multi-hop paths.

**Features:**
- Energy-aware path selection
- Dynamic neighbor discovery
- Load balancing through energy consideration

**Energy Cost Function:**
```python
cost = transmission_energy + energy_penalty
where energy_penalty = (1 - residual_energy_ratio) × transmission_energy
```

### 3. Cluster-Based Router

**Description:** Hierarchical routing through cluster heads (used by LEACH).

**Routing Path:**
```
Member → Cluster Head → Base Station
```

**Advantages:**
- Reduced long-distance transmissions
- Data aggregation opportunities
- Scalable

### 4. Adaptive Router

**Description:** Dynamically chooses between direct and multi-hop based on distance and energy.

**Decision Logic:**
```python
if distance < threshold or high_energy:
    use direct_transmission
else:
    use multi_hop
```

---

## Performance Metrics

### Network Lifetime Metrics

1. **First Node Death (FND)**
   - Round when first node depletes energy
   - Indicates stability period

2. **Half Nodes Death (HND)**
   - Round when 50% of nodes are dead
   - Network functionality threshold

3. **Last Node Death (LND)**
   - Round when all nodes are dead
   - Maximum network lifetime

### Energy Metrics

1. **Total Energy Consumed**
   ```python
   E_total = Σ(E_initial - E_current)
   ```

2. **Energy Efficiency**
   ```python
   η = Total_Packets_Delivered / Total_Energy_Consumed
   ```

3. **Energy Depletion Rate**
   ```python
   rate = ΔE / Δt
   ```

### Throughput Metrics

1. **Packets to Base Station**
   - Total packets successfully delivered

2. **Average Throughput**
   ```python
   throughput = Total_Packets / Total_Time
   ```

3. **Throughput Variance**
   - Indicates stability of data delivery

### Clustering Metrics

1. **Average Cluster Size**
2. **Cluster Head Distribution**
3. **Cluster Stability**

---

## Usage Guide

### Basic Simulation

```python
from src.network import WirelessSensorNetwork
from src.leach import LEACH
from visualization.plotter import NetworkVisualizer

# Create network
network = WirelessSensorNetwork(
    num_nodes=100,
    area_size=(100, 100),
    base_station=(50, 150),
    initial_energy=0.5
)

# Initialize LEACH
leach = LEACH(network, cluster_head_probability=0.05)

# Run simulation
for round in range(1000):
    leach.run_round()
    if network.is_dead():
        break

# Visualize
visualizer = NetworkVisualizer(network)
visualizer.plot_topology(show_clusters=True)
```

### Advanced Analysis

```python
from visualization.metrics import PerformanceAnalyzer

# After simulation
analyzer = PerformanceAnalyzer(leach.rounds_history)

# Get comprehensive report
report = analyzer.get_comprehensive_report()

# Print metrics
analyzer.print_report()

# Plot metrics over time
analyzer.plot_metrics_over_time()
```

### Parameter Sensitivity Study

```python
ch_probabilities = [0.02, 0.05, 0.08, 0.10, 0.15]
results = {}

for p in ch_probabilities:
    network = WirelessSensorNetwork(num_nodes=100, ...)
    leach = LEACH(network, cluster_head_probability=p)

    # Run simulation...

    results[p] = leach.rounds_history

# Compare results
from visualization.plotter import plot_protocol_comparison
plot_protocol_comparison(results, metric='alive_nodes')
```

---

## Configuration

### YAML Configuration

Edit `config/config.yaml` to customize parameters:

```yaml
network:
  num_nodes: 100
  area_width: 100
  area_height: 100

energy:
  initial_energy: 0.5
  E_elec: 50e-9

leach:
  cluster_head_probability: 0.05
```

### Loading Configuration

```python
import yaml

with open('config/config.yaml', 'r') as f:
    config = yaml.safe_load(f)

network = WirelessSensorNetwork(
    num_nodes=config['network']['num_nodes'],
    area_size=(config['network']['area_width'],
               config['network']['area_height']),
    initial_energy=config['energy']['initial_energy']
)
```

---

## Extending the Framework

### Adding a New Clustering Protocol

```python
from src.leach import LEACH

class MyProtocol(LEACH):
    def setup_phase(self):
        # Custom cluster head election
        self._my_custom_election()
        self._form_clusters()

    def _my_custom_election(self):
        # Implement your CH election logic
        pass
```

### Adding a New Routing Strategy

```python
from src.routing import Router

class MyRouter(Router):
    def route_packet(self, source, destination):
        # Implement your routing algorithm
        path = self._find_path(source, destination)
        return path
```

### Custom Energy Model

```python
from src.energy_model import EnergyModel

class MyEnergyModel(EnergyModel):
    def transmit_energy(self, distance, num_bits=None):
        # Custom transmission energy calculation
        return custom_energy
```

---

## Research Applications

This framework is suitable for:

1. **Protocol Comparison Studies**
   - Compare LEACH with other protocols
   - Evaluate protocol performance under different conditions

2. **Parameter Optimization**
   - Find optimal cluster head percentage
   - Optimize energy parameters

3. **Network Design**
   - Determine optimal node deployment
   - Calculate required initial energy

4. **Algorithm Development**
   - Test new clustering algorithms
   - Develop energy-efficient routing strategies

---

## References

1. Heinzelman, W.R., Chandrakasan, A., & Balakrishnan, H. (2000). "Energy-efficient communication protocol for wireless microsensor networks." Proceedings of HICSS.

2. Heinzelman, W.R., Chandrakasan, A., & Balakrishnan, H. (2002). "An application-specific protocol architecture for wireless microsensor networks." IEEE Transactions on Wireless Communications.

3. Younis, O., & Fahmy, S. (2004). "HEED: A hybrid, energy-efficient, distributed clustering approach for ad hoc sensor networks." IEEE Transactions on Mobile Computing.

---

## License

MIT License - See LICENSE file for details.

## Support

For issues and questions:
- Open an issue on GitHub
- Consult the README.md for quick start guide
- Review example scripts in the `examples/` directory
