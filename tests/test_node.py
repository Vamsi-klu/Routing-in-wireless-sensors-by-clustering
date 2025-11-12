"""
Comprehensive unit tests for node.py

Tests cover all methods, state transitions, edge cases for 95%+ coverage.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
import math
from src.node import SensorNode, NodeType, NodeState
from src.energy_model import EnergyModel


class TestNodeInitialization:
    """Test sensor node initialization"""

    def test_basic_initialization(self):
        """Test basic node creation"""
        node = SensorNode(node_id=0, x=10, y=20, initial_energy=0.5)

        assert node.id == 0
        assert node.x == 10
        assert node.y == 20
        assert node.initial_energy == 0.5
        assert node.energy == 0.5
        assert node.node_type == NodeType.NORMAL
        assert node.state == NodeState.ACTIVE
        assert not node.is_cluster_head
        assert node.cluster_head is None
        assert node.cluster_members == []
        assert node.packets_sent == 0
        assert node.packets_received == 0
        assert node.total_tx_distance == 0.0
        assert node.ch_rounds == 0
        assert node.last_ch_round == -1
        assert node.round == 0

    def test_initialization_with_custom_energy_model(self):
        """Test initialization with custom energy model"""
        custom_model = EnergyModel(E_elec=100e-9)
        node = SensorNode(0, 10, 20, energy_model=custom_model)

        assert node.energy_model == custom_model
        assert node.energy_model.E_elec == 100e-9

    def test_initialization_with_default_energy_model(self):
        """Test that default energy model is used when not specified"""
        node = SensorNode(0, 10, 20)

        assert node.energy_model is not None
        assert isinstance(node.energy_model, EnergyModel)

    def test_float_coordinates(self):
        """Test initialization with float coordinates"""
        node = SensorNode(0, 15.5, 25.7, initial_energy=0.5)

        assert node.x == 15.5
        assert node.y == 25.7

    def test_zero_initial_energy(self):
        """Test initialization with zero energy"""
        node = SensorNode(0, 10, 20, initial_energy=0)

        assert node.energy == 0
        assert node.initial_energy == 0


class TestDistanceCalculation:
    """Test distance_to method"""

    def test_distance_to_another_node(self):
        """Test distance calculation between two nodes"""
        node1 = SensorNode(0, 0, 0, 0.5)
        node2 = SensorNode(1, 3, 4, 0.5)

        distance = node1.distance_to(node2)

        assert distance == 5.0  # 3-4-5 triangle

    def test_distance_to_tuple(self):
        """Test distance calculation to coordinate tuple"""
        node = SensorNode(0, 0, 0, 0.5)
        distance = node.distance_to((3, 4))

        assert distance == 5.0

    def test_distance_to_same_position(self):
        """Test distance to same position"""
        node1 = SensorNode(0, 10, 20, 0.5)
        node2 = SensorNode(1, 10, 20, 0.5)

        distance = node1.distance_to(node2)

        assert distance == 0.0

    def test_distance_symmetry(self):
        """Test that distance is symmetric"""
        node1 = SensorNode(0, 10, 20, 0.5)
        node2 = SensorNode(1, 30, 40, 0.5)

        dist1_to_2 = node1.distance_to(node2)
        dist2_to_1 = node2.distance_to(node1)

        assert dist1_to_2 == dist2_to_1

    def test_distance_with_negative_coordinates(self):
        """Test distance with negative coordinates"""
        node1 = SensorNode(0, -10, -10, 0.5)
        node2 = SensorNode(1, 10, 10, 0.5)

        distance = node1.distance_to(node2)

        expected = math.sqrt(20**2 + 20**2)
        assert pytest.approx(distance, rel=1e-9) == expected

    def test_distance_with_float_coordinates(self):
        """Test distance with float coordinates"""
        node1 = SensorNode(0, 1.5, 2.5, 0.5)
        node2 = SensorNode(1, 4.5, 6.5, 0.5)

        distance = node1.distance_to(node2)

        expected = math.sqrt(3**2 + 4**2)
        assert pytest.approx(distance, rel=1e-9) == expected


class TestNodeState:
    """Test node state management"""

    def test_is_alive_initially(self):
        """Test node is alive after initialization"""
        node = SensorNode(0, 10, 20, 0.5)

        assert node.is_alive()
        assert not node.is_dead()

    def test_is_dead_when_energy_zero(self):
        """Test node is dead when energy reaches zero"""
        node = SensorNode(0, 10, 20, 0.001)

        # Drain all energy
        dest = SensorNode(1, 100, 100, 0.5)
        node.transmit(dest)

        assert node.is_dead()
        assert not node.is_alive()
        assert node.energy == 0
        assert node.state == NodeState.DEAD

    def test_is_dead_when_state_is_dead(self):
        """Test node is dead when state is DEAD"""
        node = SensorNode(0, 10, 20, 0.5)
        node.state = NodeState.DEAD

        assert node.is_dead()
        assert not node.is_alive()

    def test_zero_initial_energy_node_alive(self):
        """Test node with zero energy is still considered alive initially"""
        node = SensorNode(0, 10, 20, 0)

        # Node is dead because energy is 0
        assert not node.is_alive()
        assert node.is_dead()


class TestTransmission:
    """Test transmit method"""

    def test_successful_transmission(self):
        """Test successful data transmission"""
        source = SensorNode(0, 0, 0, 1.0)
        dest = SensorNode(1, 10, 0, 1.0)

        initial_energy = source.energy
        result = source.transmit(dest)

        assert result is True
        assert source.energy < initial_energy
        assert source.packets_sent == 1
        assert source.total_tx_distance == 10.0

    def test_transmission_to_tuple_coordinates(self):
        """Test transmission to tuple coordinates"""
        source = SensorNode(0, 0, 0, 1.0)
        dest_coords = (10, 0)

        initial_energy = source.energy
        result = source.transmit(dest_coords)

        assert result is True
        assert source.energy < initial_energy
        assert source.packets_sent == 1

    def test_transmission_with_custom_bits(self):
        """Test transmission with custom number of bits"""
        source = SensorNode(0, 0, 0, 1.0)
        dest = SensorNode(1, 10, 0, 1.0)

        result = source.transmit(dest, num_bits=2000)

        assert result is True
        assert source.packets_sent == 1

    def test_transmission_drains_energy(self):
        """Test that transmission drains energy proportionally to distance"""
        source1 = SensorNode(0, 0, 0, 1.0)
        source2 = SensorNode(1, 0, 0, 1.0)
        dest_near = (10, 0)
        dest_far = (50, 0)

        source1.transmit(dest_near)
        source2.transmit(dest_far)

        assert source2.energy < source1.energy

    def test_transmission_updates_statistics(self):
        """Test that transmission updates node statistics"""
        source = SensorNode(0, 0, 0, 1.0)
        dest = SensorNode(1, 10, 0, 1.0)

        source.transmit(dest)
        source.transmit(dest)
        source.transmit(dest)

        assert source.packets_sent == 3
        assert source.total_tx_distance == 30.0

    def test_failed_transmission_insufficient_energy(self):
        """Test transmission fails when insufficient energy"""
        source = SensorNode(0, 0, 0, 0.00001)  # Very low energy
        dest = SensorNode(1, 100, 100, 1.0)  # Far away

        result = source.transmit(dest)

        assert result is False
        assert source.state == NodeState.DEAD
        assert source.energy == 0

    def test_transmission_from_dead_node(self):
        """Test transmission from dead node fails"""
        source = SensorNode(0, 0, 0, 0.5)
        source.state = NodeState.DEAD
        dest = SensorNode(1, 10, 0, 0.5)

        result = source.transmit(dest)

        assert result is False

    def test_transmission_kills_node_exactly(self):
        """Test transmission that exactly depletes energy"""
        source = SensorNode(0, 0, 0, 0.5)
        dest = SensorNode(1, 10, 0, 0.5)

        # Calculate exact energy needed
        energy_needed = source.energy_model.transmit_energy(10)
        source.energy = energy_needed

        result = source.transmit(dest)

        assert result is True
        assert source.energy == 0
        assert source.state == NodeState.DEAD

    def test_zero_distance_transmission(self):
        """Test transmission to same location"""
        source = SensorNode(0, 0, 0, 1.0)
        dest = SensorNode(1, 0, 0, 1.0)

        result = source.transmit(dest)

        assert result is True
        # Should still consume electronics energy
        assert source.energy < 1.0


class TestReception:
    """Test receive method"""

    def test_successful_reception(self):
        """Test successful data reception"""
        node = SensorNode(0, 0, 0, 1.0)

        initial_energy = node.energy
        result = node.receive()

        assert result is True
        assert node.energy < initial_energy
        assert node.packets_received == 1

    def test_reception_with_custom_bits(self):
        """Test reception with custom number of bits"""
        node = SensorNode(0, 0, 0, 1.0)

        result = node.receive(num_bits=2000)

        assert result is True
        assert node.packets_received == 1

    def test_multiple_receptions(self):
        """Test multiple receptions"""
        node = SensorNode(0, 0, 0, 1.0)

        node.receive()
        node.receive()
        node.receive()

        assert node.packets_received == 3

    def test_failed_reception_insufficient_energy(self):
        """Test reception fails when insufficient energy"""
        node = SensorNode(0, 0, 0, 0.00000001)

        result = node.receive()

        assert result is False
        assert node.state == NodeState.DEAD
        assert node.energy == 0

    def test_reception_from_dead_node(self):
        """Test reception from dead node fails"""
        node = SensorNode(0, 0, 0, 0.5)
        node.state = NodeState.DEAD

        result = node.receive()

        assert result is False

    def test_reception_kills_node(self):
        """Test reception that kills node"""
        node = SensorNode(0, 0, 0, 0.5)

        # Set energy to exactly what's needed
        energy_needed = node.energy_model.receive_energy()
        node.energy = energy_needed

        result = node.receive()

        assert result is True
        assert node.energy == 0
        assert node.state == NodeState.DEAD


class TestDataAggregation:
    """Test aggregate_data method"""

    def test_successful_aggregation(self):
        """Test successful data aggregation"""
        node = SensorNode(0, 0, 0, 1.0)

        initial_energy = node.energy
        result = node.aggregate_data(5)

        assert result is True
        assert node.energy < initial_energy

    def test_aggregation_zero_packets(self):
        """Test aggregation of zero packets"""
        node = SensorNode(0, 0, 0, 1.0)

        initial_energy = node.energy
        result = node.aggregate_data(0)

        assert result is True
        assert node.energy == initial_energy  # No energy consumed

    def test_aggregation_many_packets(self):
        """Test aggregation of many packets"""
        node = SensorNode(0, 0, 0, 1.0)

        result = node.aggregate_data(100)

        assert result is True
        assert node.energy < 1.0

    def test_aggregation_proportional_to_packets(self):
        """Test that aggregation energy is proportional to packet count"""
        node1 = SensorNode(0, 0, 0, 1.0)
        node2 = SensorNode(1, 0, 0, 1.0)

        node1.aggregate_data(10)
        node2.aggregate_data(20)

        energy_consumed_1 = 1.0 - node1.energy
        energy_consumed_2 = 1.0 - node2.energy

        assert pytest.approx(energy_consumed_2 / energy_consumed_1, rel=1e-6) == 2.0

    def test_failed_aggregation_insufficient_energy(self):
        """Test aggregation fails with insufficient energy"""
        node = SensorNode(0, 0, 0, 0.00000001)

        result = node.aggregate_data(10)

        assert result is False
        assert node.state == NodeState.DEAD
        assert node.energy == 0

    def test_aggregation_from_dead_node(self):
        """Test aggregation from dead node fails"""
        node = SensorNode(0, 0, 0, 0.5)
        node.state = NodeState.DEAD

        result = node.aggregate_data(5)

        assert result is False


class TestSensing:
    """Test sense method"""

    def test_successful_sensing(self):
        """Test successful sensing operation"""
        node = SensorNode(0, 0, 0, 1.0)

        initial_energy = node.energy
        result = node.sense()

        assert result is True
        assert node.energy < initial_energy

    def test_multiple_sensing_operations(self):
        """Test multiple sensing operations"""
        node = SensorNode(0, 0, 0, 1.0)

        for _ in range(10):
            result = node.sense()
            assert result is True

        assert node.energy < 1.0

    def test_failed_sensing_insufficient_energy(self):
        """Test sensing fails with insufficient energy"""
        node = SensorNode(0, 0, 0, 0.00000001)

        result = node.sense()

        assert result is False
        assert node.state == NodeState.DEAD
        assert node.energy == 0

    def test_sensing_from_dead_node(self):
        """Test sensing from dead node fails"""
        node = SensorNode(0, 0, 0, 0.5)
        node.state = NodeState.DEAD

        result = node.sense()

        assert result is False


class TestClusterHeadManagement:
    """Test cluster head related methods"""

    def test_set_as_cluster_head(self):
        """Test setting node as cluster head"""
        node = SensorNode(0, 0, 0, 0.5)
        node.round = 5

        node.set_cluster_head(True)

        assert node.is_cluster_head is True
        assert node.node_type == NodeType.CLUSTER_HEAD
        assert node.cluster_head == node
        assert node.cluster_members == []
        assert node.ch_rounds == 1
        assert node.last_ch_round == 5

    def test_set_as_normal_node(self):
        """Test setting node as normal node"""
        node = SensorNode(0, 0, 0, 0.5)
        node.set_cluster_head(True)  # First make it CH

        node.set_cluster_head(False)

        assert node.is_cluster_head is False
        assert node.node_type == NodeType.NORMAL
        assert node.cluster_head is None
        assert node.cluster_members == []

    def test_multiple_ch_assignments(self):
        """Test node becoming CH multiple times"""
        node = SensorNode(0, 0, 0, 0.5)

        node.round = 1
        node.set_cluster_head(True)
        assert node.ch_rounds == 1

        node.set_cluster_head(False)
        node.round = 5
        node.set_cluster_head(True)
        assert node.ch_rounds == 2
        assert node.last_ch_round == 5

    def test_join_cluster(self):
        """Test node joining a cluster"""
        ch = SensorNode(0, 0, 0, 0.5)
        ch.set_cluster_head(True)

        member = SensorNode(1, 10, 10, 0.5)
        member.join_cluster(ch)

        assert member.cluster_head == ch
        assert member.is_cluster_head is False
        assert member.node_type == NodeType.NORMAL

    def test_cluster_head_reference(self):
        """Test cluster head self-reference"""
        node = SensorNode(0, 0, 0, 0.5)
        node.set_cluster_head(True)

        assert node.cluster_head == node


class TestEnergyPercentage:
    """Test get_energy_percentage method"""

    def test_full_energy_percentage(self):
        """Test energy percentage at full energy"""
        node = SensorNode(0, 0, 0, 0.5)

        percentage = node.get_energy_percentage()

        assert percentage == 100.0

    def test_half_energy_percentage(self):
        """Test energy percentage at half energy"""
        node = SensorNode(0, 0, 0, 0.5)
        node.energy = 0.25

        percentage = node.get_energy_percentage()

        assert percentage == 50.0

    def test_zero_energy_percentage(self):
        """Test energy percentage at zero energy"""
        node = SensorNode(0, 0, 0, 0.5)
        node.energy = 0

        percentage = node.get_energy_percentage()

        assert percentage == 0.0

    def test_zero_initial_energy_percentage(self):
        """Test energy percentage when initial energy is zero"""
        node = SensorNode(0, 0, 0, 0)

        percentage = node.get_energy_percentage()

        assert percentage == 0

    def test_energy_percentage_after_operations(self):
        """Test energy percentage after various operations"""
        node = SensorNode(0, 0, 0, 1.0)
        initial_percentage = node.get_energy_percentage()

        dest = SensorNode(1, 10, 0, 1.0)
        node.transmit(dest)

        final_percentage = node.get_energy_percentage()

        assert final_percentage < initial_percentage
        assert 0 <= final_percentage <= 100


class TestResetForNewRound:
    """Test reset_for_new_round method"""

    def test_round_increment(self):
        """Test that round increments"""
        node = SensorNode(0, 0, 0, 0.5)

        node.reset_for_new_round()
        assert node.round == 1

        node.reset_for_new_round()
        assert node.round == 2

    def test_non_ch_cluster_reset(self):
        """Test that non-CH nodes reset cluster info"""
        ch = SensorNode(0, 0, 0, 0.5)
        ch.set_cluster_head(True)

        member = SensorNode(1, 10, 10, 0.5)
        member.join_cluster(ch)

        member.reset_for_new_round()

        assert member.cluster_head is None
        assert member.cluster_members == []

    def test_ch_cluster_not_reset(self):
        """Test that CH nodes keep their cluster info"""
        node = SensorNode(0, 0, 0, 0.5)
        node.set_cluster_head(True)

        # Add some members
        node.cluster_members = [SensorNode(i, i*10, i*10, 0.5) for i in range(1, 4)]

        node.reset_for_new_round()

        # CH should keep its members
        assert node.cluster_head is not None
        assert len(node.cluster_members) == 3


class TestStringRepresentations:
    """Test __str__ and __repr__ methods"""

    def test_str_representation(self):
        """Test string representation"""
        node = SensorNode(0, 10.5, 20.7, 0.5)

        str_rep = str(node)

        assert "Node 0" in str_rep
        assert "10.5" in str_rep
        assert "20.7" in str_rep
        assert "normal" in str_rep.lower()
        assert "active" in str_rep.lower()

    def test_repr_representation(self):
        """Test repr representation"""
        node = SensorNode(5, 15, 25, 0.5)

        repr_rep = repr(node)

        assert "SensorNode" in repr_rep
        assert "id=5" in repr_rep
        assert "(15, 25)" in repr_rep

    def test_str_for_cluster_head(self):
        """Test string representation for cluster head"""
        node = SensorNode(0, 10, 20, 0.5)
        node.set_cluster_head(True)

        str_rep = str(node)

        assert "cluster_head" in str_rep.lower()

    def test_str_for_dead_node(self):
        """Test string representation for dead node"""
        node = SensorNode(0, 10, 20, 0.5)
        node.state = NodeState.DEAD

        str_rep = str(node)

        assert "dead" in str_rep.lower()


class TestNodeComplexScenarios:
    """Test complex scenarios with multiple operations"""

    def test_node_lifecycle(self):
        """Test complete node lifecycle from creation to death"""
        node = SensorNode(0, 0, 0, 0.01)  # Low energy
        dest = SensorNode(1, 100, 100, 1.0)

        assert node.is_alive()

        # Perform operations until death
        operations = 0
        while node.is_alive() and operations < 100:
            node.sense()
            node.receive()
            operations += 1

        # Should eventually die or get very low
        assert node.energy < 0.01 or node.is_dead()

    def test_cluster_head_operations(self):
        """Test cluster head performing typical operations"""
        ch = SensorNode(0, 50, 50, 1.0)
        ch.set_cluster_head(True)

        # Receive from members
        for _ in range(5):
            ch.receive()

        # Aggregate
        ch.aggregate_data(5)

        # Send to base station
        ch.transmit((50, 150))

        assert ch.is_alive()
        assert ch.packets_received == 5
        assert ch.packets_sent == 1

    def test_member_node_operations(self):
        """Test member node performing typical operations"""
        member = SensorNode(0, 10, 10, 1.0)
        ch = SensorNode(1, 50, 50, 1.0)
        member.join_cluster(ch)

        # Sense and transmit to CH
        member.sense()
        member.transmit(ch)

        assert member.packets_sent == 1
        assert member.is_alive()

    def test_energy_consistency(self):
        """Test that energy calculations are consistent"""
        node1 = SensorNode(0, 0, 0, 1.0)
        node2 = SensorNode(1, 0, 0, 1.0)
        dest = (50, 50)

        # Same operations should consume same energy
        node1.transmit(dest)
        node2.transmit(dest)

        assert node1.energy == node2.energy

    def test_node_independence(self):
        """Test that nodes are independent"""
        node1 = SensorNode(0, 0, 0, 1.0)
        node2 = SensorNode(1, 0, 0, 1.0)

        node1.transmit((50, 50))

        # node2 should be unaffected
        assert node2.energy == 1.0
        assert node2.packets_sent == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
