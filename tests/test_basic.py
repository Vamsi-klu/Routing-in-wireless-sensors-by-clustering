"""
Basic unit tests for WSN components
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.node import SensorNode, NodeType, NodeState
from src.network import WirelessSensorNetwork
from src.energy_model import EnergyModel
from src.leach import LEACH


def test_node_creation():
    """Test sensor node creation"""
    node = SensorNode(node_id=0, x=10, y=20, initial_energy=0.5)

    assert node.id == 0
    assert node.x == 10
    assert node.y == 20
    assert node.energy == 0.5
    assert node.is_alive()
    assert not node.is_dead()
    assert node.node_type == NodeType.NORMAL


def test_node_distance():
    """Test distance calculation between nodes"""
    node1 = SensorNode(0, 0, 0, 0.5)
    node2 = SensorNode(1, 3, 4, 0.5)

    distance = node1.distance_to(node2)
    assert distance == 5.0  # 3-4-5 triangle


def test_node_energy_consumption():
    """Test node energy consumption"""
    node = SensorNode(0, 0, 0, initial_energy=1.0)
    initial_energy = node.energy

    # Create a destination
    dest = SensorNode(1, 10, 0, 1.0)

    # Transmit
    success = node.transmit(dest)
    assert success
    assert node.energy < initial_energy


def test_network_creation():
    """Test network creation"""
    network = WirelessSensorNetwork(
        num_nodes=10,
        area_size=(100, 100),
        base_station=(50, 150),
        initial_energy=0.5
    )

    assert len(network.nodes) == 10
    assert network.area_width == 100
    assert network.area_height == 100
    assert network.base_station == (50, 150)

    # All nodes should be alive initially
    assert len(network.get_alive_nodes()) == 10
    assert len(network.get_dead_nodes()) == 0


def test_energy_model():
    """Test energy model calculations"""
    model = EnergyModel()

    # Test transmission energy calculation
    distance = 10  # meters
    energy = model.transmit_energy(distance)

    assert energy > 0

    # Longer distance should consume more energy
    energy_long = model.transmit_energy(50)
    assert energy_long > energy

    # Test receive energy
    rx_energy = model.receive_energy()
    assert rx_energy > 0


def test_leach_initialization():
    """Test LEACH protocol initialization"""
    network = WirelessSensorNetwork(
        num_nodes=20,
        area_size=(100, 100),
        base_station=(50, 150)
    )

    leach = LEACH(network, cluster_head_probability=0.1)

    assert leach.p == 0.1
    assert leach.current_round == 0
    assert len(leach.cluster_heads) == 0


def test_leach_round():
    """Test running one LEACH round"""
    network = WirelessSensorNetwork(
        num_nodes=20,
        area_size=(100, 100),
        base_station=(50, 150),
        initial_energy=0.5
    )

    leach = LEACH(network, cluster_head_probability=0.1)

    # Run one round
    stats = leach.run_round()

    assert leach.current_round == 1
    assert 'round' in stats
    assert 'num_cluster_heads' in stats
    assert 'alive_nodes' in stats
    assert stats['alive_nodes'] <= 20


def test_cluster_head_election():
    """Test cluster head election"""
    network = WirelessSensorNetwork(
        num_nodes=50,
        area_size=(100, 100),
        base_station=(50, 150),
        initial_energy=0.5
    )

    leach = LEACH(network, cluster_head_probability=0.05)
    leach.setup_phase()

    # Should have elected some cluster heads
    assert len(leach.cluster_heads) > 0

    # Cluster heads should be marked correctly
    for ch in leach.cluster_heads:
        assert ch.is_cluster_head
        assert ch.node_type == NodeType.CLUSTER_HEAD


def test_network_statistics():
    """Test network statistics calculation"""
    network = WirelessSensorNetwork(
        num_nodes=30,
        area_size=(100, 100),
        base_station=(50, 150),
        initial_energy=0.5
    )

    stats = network.get_network_statistics()

    assert stats['total_nodes'] == 30
    assert stats['alive_nodes'] == 30
    assert stats['dead_nodes'] == 0
    assert stats['alive_percentage'] == 100.0


if __name__ == "__main__":
    print("Running tests...")

    test_node_creation()
    print("✓ Node creation test passed")

    test_node_distance()
    print("✓ Node distance test passed")

    test_node_energy_consumption()
    print("✓ Energy consumption test passed")

    test_network_creation()
    print("✓ Network creation test passed")

    test_energy_model()
    print("✓ Energy model test passed")

    test_leach_initialization()
    print("✓ LEACH initialization test passed")

    test_leach_round()
    print("✓ LEACH round test passed")

    test_cluster_head_election()
    print("✓ Cluster head election test passed")

    test_network_statistics()
    print("✓ Network statistics test passed")

    print("\n✅ All tests passed!")
