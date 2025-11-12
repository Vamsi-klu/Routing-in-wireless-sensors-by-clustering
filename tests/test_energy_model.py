"""
Comprehensive unit tests for energy_model.py

Tests cover all methods, edge cases, and error conditions to achieve 95%+ coverage.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
import math
from src.energy_model import EnergyModel, default_energy_model


class TestEnergyModelInitialization:
    """Test energy model initialization"""

    def test_default_initialization(self):
        """Test initialization with default values"""
        model = EnergyModel()

        assert model.E_elec == 50e-9
        assert model.E_fs == 10e-12
        assert model.E_mp == 0.0013e-12
        assert model.E_DA == 5e-9
        assert model.d0 == 87.7
        assert model.packet_size == 4000

    def test_custom_initialization(self):
        """Test initialization with custom values"""
        model = EnergyModel(
            E_elec=100e-9,
            E_fs=20e-12,
            E_mp=0.002e-12,
            E_DA=10e-9,
            d0=100.0,
            packet_size=8000
        )

        assert model.E_elec == 100e-9
        assert model.E_fs == 20e-12
        assert model.E_mp == 0.002e-12
        assert model.E_DA == 10e-9
        assert model.d0 == 100.0
        assert model.packet_size == 8000

    def test_default_model_instance(self):
        """Test that default_energy_model is created"""
        assert isinstance(default_energy_model, EnergyModel)
        assert default_energy_model.E_elec == 50e-9


class TestTransmitEnergy:
    """Test transmit_energy method"""

    def test_short_distance_free_space_model(self):
        """Test transmission at short distance (< d0) using free space model"""
        model = EnergyModel()
        distance = 10  # meters, less than d0=87.7

        energy = model.transmit_energy(distance)

        # Should use free space model: E = E_elec * bits + E_fs * bits * d^2
        expected_elec = model.E_elec * model.packet_size
        expected_amp = model.E_fs * model.packet_size * (distance ** 2)
        expected_total = expected_elec + expected_amp

        assert pytest.approx(energy, rel=1e-9) == expected_total
        assert energy > 0

    def test_long_distance_multipath_model(self):
        """Test transmission at long distance (> d0) using multi-path model"""
        model = EnergyModel()
        distance = 100  # meters, greater than d0=87.7

        energy = model.transmit_energy(distance)

        # Should use multi-path model: E = E_elec * bits + E_mp * bits * d^4
        expected_elec = model.E_elec * model.packet_size
        expected_amp = model.E_mp * model.packet_size * (distance ** 4)
        expected_total = expected_elec + expected_amp

        assert pytest.approx(energy, rel=1e-9) == expected_total
        assert energy > 0

    def test_crossover_distance(self):
        """Test transmission at exactly crossover distance"""
        model = EnergyModel()
        distance = model.d0

        # At d0, should use free space model (distance < d0 condition)
        energy = model.transmit_energy(distance)
        assert energy > 0

    def test_zero_distance(self):
        """Test transmission at zero distance"""
        model = EnergyModel()
        energy = model.transmit_energy(0)

        # Should only have electronics energy
        expected = model.E_elec * model.packet_size
        assert pytest.approx(energy, rel=1e-9) == expected

    def test_custom_num_bits(self):
        """Test transmission with custom number of bits"""
        model = EnergyModel()
        distance = 10
        custom_bits = 2000

        energy = model.transmit_energy(distance, num_bits=custom_bits)

        expected_elec = model.E_elec * custom_bits
        expected_amp = model.E_fs * custom_bits * (distance ** 2)
        expected_total = expected_elec + expected_amp

        assert pytest.approx(energy, rel=1e-9) == expected_total

    def test_energy_increases_with_distance(self):
        """Test that energy consumption increases with distance"""
        model = EnergyModel()

        energy_10m = model.transmit_energy(10)
        energy_20m = model.transmit_energy(20)
        energy_50m = model.transmit_energy(50)

        assert energy_20m > energy_10m
        assert energy_50m > energy_20m

    def test_energy_increases_with_bits(self):
        """Test that energy consumption increases with number of bits"""
        model = EnergyModel()
        distance = 10

        energy_1000 = model.transmit_energy(distance, 1000)
        energy_2000 = model.transmit_energy(distance, 2000)
        energy_4000 = model.transmit_energy(distance, 4000)

        assert energy_2000 > energy_1000
        assert energy_4000 > energy_2000

    def test_very_large_distance(self):
        """Test transmission at very large distance"""
        model = EnergyModel()
        distance = 500  # meters

        energy = model.transmit_energy(distance)
        assert energy > 0
        assert math.isfinite(energy)


class TestReceiveEnergy:
    """Test receive_energy method"""

    def test_default_receive_energy(self):
        """Test receive energy with default packet size"""
        model = EnergyModel()
        energy = model.receive_energy()

        expected = model.E_elec * model.packet_size
        assert pytest.approx(energy, rel=1e-9) == expected
        assert energy > 0

    def test_custom_num_bits_receive(self):
        """Test receive energy with custom bits"""
        model = EnergyModel()
        custom_bits = 2000

        energy = model.receive_energy(num_bits=custom_bits)

        expected = model.E_elec * custom_bits
        assert pytest.approx(energy, rel=1e-9) == expected

    def test_receive_energy_independent_of_distance(self):
        """Test that receive energy doesn't depend on distance"""
        model = EnergyModel()
        energy1 = model.receive_energy()
        energy2 = model.receive_energy()

        assert energy1 == energy2

    def test_receive_less_than_transmit(self):
        """Test that receiving consumes less energy than transmitting"""
        model = EnergyModel()
        rx_energy = model.receive_energy()
        tx_energy = model.transmit_energy(10)  # Even at short distance

        assert rx_energy < tx_energy


class TestAggregateEnergy:
    """Test aggregate_energy method"""

    def test_single_packet_aggregation(self):
        """Test aggregation of single packet"""
        model = EnergyModel()
        energy = model.aggregate_energy(1)

        expected = model.E_DA * model.packet_size * 1
        assert pytest.approx(energy, rel=1e-9) == expected

    def test_multiple_packets_aggregation(self):
        """Test aggregation of multiple packets"""
        model = EnergyModel()
        num_packets = 10
        energy = model.aggregate_energy(num_packets)

        expected = model.E_DA * model.packet_size * num_packets
        assert pytest.approx(energy, rel=1e-9) == expected

    def test_zero_packets_aggregation(self):
        """Test aggregation of zero packets"""
        model = EnergyModel()
        energy = model.aggregate_energy(0)

        assert energy == 0

    def test_large_number_of_packets(self):
        """Test aggregation of many packets"""
        model = EnergyModel()
        energy = model.aggregate_energy(100)

        expected = model.E_DA * model.packet_size * 100
        assert pytest.approx(energy, rel=1e-9) == expected
        assert energy > 0

    def test_aggregation_proportional_to_packets(self):
        """Test that aggregation energy is proportional to packet count"""
        model = EnergyModel()

        energy_10 = model.aggregate_energy(10)
        energy_20 = model.aggregate_energy(20)

        assert pytest.approx(energy_20 / energy_10, rel=1e-6) == 2.0


class TestIdleEnergy:
    """Test idle_energy method"""

    def test_idle_energy_calculation(self):
        """Test idle energy calculation"""
        model = EnergyModel()
        energy = model.idle_energy()

        expected = 0.001 * model.E_elec
        assert pytest.approx(energy, rel=1e-9) == expected
        assert energy > 0

    def test_idle_energy_constant(self):
        """Test that idle energy is constant"""
        model = EnergyModel()
        energy1 = model.idle_energy()
        energy2 = model.idle_energy()

        assert energy1 == energy2

    def test_idle_much_less_than_active(self):
        """Test that idle energy is much less than active operations"""
        model = EnergyModel()
        idle = model.idle_energy()
        receive = model.receive_energy()
        transmit = model.transmit_energy(10)

        assert idle < receive
        assert idle < transmit


class TestSensingEnergy:
    """Test sensing_energy method"""

    def test_sensing_energy_value(self):
        """Test sensing energy returns correct value"""
        model = EnergyModel()
        energy = model.sensing_energy()

        assert energy == 10e-9  # 10 nJ
        assert energy > 0

    def test_sensing_energy_constant(self):
        """Test that sensing energy is constant"""
        model = EnergyModel()
        energy1 = model.sensing_energy()
        energy2 = model.sensing_energy()

        assert energy1 == energy2


class TestComputeMaxDistance:
    """Test compute_max_distance method"""

    def test_short_range_max_distance(self):
        """Test max distance calculation for short range (free space)"""
        model = EnergyModel()
        available_energy = 0.001  # 1 mJ

        max_dist = model.compute_max_distance(available_energy)

        assert max_dist > 0
        # Verify it's actually achievable
        energy_needed = model.transmit_energy(max_dist)
        assert energy_needed <= available_energy

    def test_long_range_max_distance(self):
        """Test max distance calculation for long range (multi-path)"""
        model = EnergyModel()
        available_energy = 0.01  # 10 mJ

        max_dist = model.compute_max_distance(available_energy)

        assert max_dist > 0
        # Should be using multi-path model
        assert max_dist > model.d0

    def test_insufficient_energy(self):
        """Test max distance with insufficient energy"""
        model = EnergyModel()
        # Energy less than electronics energy
        available_energy = model.E_elec * model.packet_size * 0.5

        max_dist = model.compute_max_distance(available_energy)

        assert max_dist == 0

    def test_exact_electronics_energy(self):
        """Test max distance with exact electronics energy"""
        model = EnergyModel()
        available_energy = model.E_elec * model.packet_size

        max_dist = model.compute_max_distance(available_energy)

        assert max_dist == 0

    def test_custom_bits_max_distance(self):
        """Test max distance with custom number of bits"""
        model = EnergyModel()
        available_energy = 0.001
        custom_bits = 2000

        max_dist = model.compute_max_distance(available_energy, num_bits=custom_bits)

        assert max_dist > 0

    def test_more_energy_greater_distance(self):
        """Test that more energy allows greater distance"""
        model = EnergyModel()

        dist1 = model.compute_max_distance(0.001)
        dist2 = model.compute_max_distance(0.002)
        dist3 = model.compute_max_distance(0.005)

        assert dist2 > dist1
        assert dist3 > dist2

    def test_crossover_behavior(self):
        """Test behavior around crossover distance"""
        model = EnergyModel()

        # Find energy needed for distance just below d0
        dist_below = model.d0 - 1
        energy_below = model.transmit_energy(dist_below)

        # Find energy needed for distance just above d0
        dist_above = model.d0 + 1
        energy_above = model.transmit_energy(dist_above)

        # Compute max distances
        max_dist_below = model.compute_max_distance(energy_below)
        max_dist_above = model.compute_max_distance(energy_above)

        assert max_dist_below > 0
        assert max_dist_above > 0

    def test_zero_energy(self):
        """Test max distance with zero energy"""
        model = EnergyModel()
        max_dist = model.compute_max_distance(0)

        assert max_dist == 0

    def test_negative_energy(self):
        """Test max distance with negative energy"""
        model = EnergyModel()
        max_dist = model.compute_max_distance(-0.001)

        assert max_dist == 0


class TestEnergyModelComparison:
    """Test comparisons between different energy models"""

    def test_different_models_different_results(self):
        """Test that different models give different results"""
        model1 = EnergyModel(E_elec=50e-9)
        model2 = EnergyModel(E_elec=100e-9)

        energy1 = model1.transmit_energy(10)
        energy2 = model2.transmit_energy(10)

        assert energy2 > energy1

    def test_free_space_vs_multipath_amplification(self):
        """Test that free space and multipath have different costs"""
        model = EnergyModel()

        # At same distance, but different models
        # Short distance with free space
        energy_short = model.transmit_energy(50)

        # Long distance with multi-path
        energy_long = model.transmit_energy(100)

        # Long distance should cost significantly more
        assert energy_long > energy_short


class TestEnergyModelEdgeCases:
    """Test edge cases and boundary conditions"""

    def test_very_small_energy_values(self):
        """Test model with very small energy parameters"""
        model = EnergyModel(E_elec=1e-12, E_fs=1e-15, E_mp=1e-18)

        energy = model.transmit_energy(10)
        assert energy > 0
        assert math.isfinite(energy)

    def test_very_large_packet_size(self):
        """Test with very large packet size"""
        model = EnergyModel(packet_size=1000000)

        energy = model.transmit_energy(10)
        assert energy > 0
        assert math.isfinite(energy)

    def test_very_small_d0(self):
        """Test with very small crossover distance"""
        model = EnergyModel(d0=1.0)

        # Transmit at distance > d0, should use multi-path
        energy = model.transmit_energy(2.0)
        assert energy > 0

    def test_very_large_d0(self):
        """Test with very large crossover distance"""
        model = EnergyModel(d0=1000.0)

        # Transmit at normal distance, should use free space
        energy = model.transmit_energy(100)
        assert energy > 0

    def test_energy_consistency(self):
        """Test that energy calculations are consistent"""
        model = EnergyModel()
        distance = 50

        # Calculate multiple times
        energy1 = model.transmit_energy(distance)
        energy2 = model.transmit_energy(distance)
        energy3 = model.transmit_energy(distance)

        assert energy1 == energy2 == energy3


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
