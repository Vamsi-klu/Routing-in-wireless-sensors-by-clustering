"""
Energy Model for Wireless Sensor Networks

Implements the first-order radio energy model commonly used in WSN research.
Based on the energy dissipation model from LEACH paper.
"""

import math


class EnergyModel:
    """
    First-order radio energy model for WSN.

    Energy dissipation for transmitting/receiving k-bit message over distance d:
    - E_tx = E_elec * k + E_amp * k * d^n
    - E_rx = E_elec * k
    """

    def __init__(self,
                 E_elec=50e-9,      # Energy to run transmitter/receiver circuit (50 nJ/bit)
                 E_fs=10e-12,       # Free space amplifier energy (10 pJ/bit/m^2)
                 E_mp=0.0013e-12,   # Multi-path amplifier energy (0.0013 pJ/bit/m^4)
                 E_DA=5e-9,         # Data aggregation energy (5 nJ/bit/signal)
                 d0=87.7,           # Crossover distance (m)
                 packet_size=4000): # Packet size in bits
        """
        Initialize energy model with radio parameters.

        Args:
            E_elec: Electronics energy (J/bit)
            E_fs: Free space amplification energy (J/bit/m^2)
            E_mp: Multi-path amplification energy (J/bit/m^4)
            E_DA: Data aggregation energy (J/bit/signal)
            d0: Crossover distance between free space and multi-path model (m)
            packet_size: Default packet size (bits)
        """
        self.E_elec = E_elec
        self.E_fs = E_fs
        self.E_mp = E_mp
        self.E_DA = E_DA
        self.d0 = d0
        self.packet_size = packet_size

    def transmit_energy(self, distance, num_bits=None):
        """
        Calculate energy consumed for transmitting data.

        Uses free space model (d^2) for short distances and
        multi-path model (d^4) for long distances.

        Args:
            distance: Transmission distance (m)
            num_bits: Number of bits to transmit (default: packet_size)

        Returns:
            Energy consumed in Joules
        """
        if num_bits is None:
            num_bits = self.packet_size

        # Electronics energy
        e_elec = self.E_elec * num_bits

        # Amplification energy (depends on distance)
        if distance < self.d0:
            # Free space model (d^2)
            e_amp = self.E_fs * num_bits * (distance ** 2)
        else:
            # Multi-path fading model (d^4)
            e_amp = self.E_mp * num_bits * (distance ** 4)

        return e_elec + e_amp

    def receive_energy(self, num_bits=None):
        """
        Calculate energy consumed for receiving data.

        Args:
            num_bits: Number of bits to receive (default: packet_size)

        Returns:
            Energy consumed in Joules
        """
        if num_bits is None:
            num_bits = self.packet_size

        return self.E_elec * num_bits

    def aggregate_energy(self, num_packets):
        """
        Calculate energy consumed for data aggregation.

        Args:
            num_packets: Number of packets to aggregate

        Returns:
            Energy consumed in Joules
        """
        return self.E_DA * self.packet_size * num_packets

    def idle_energy(self):
        """
        Calculate energy consumed in idle state per time unit.

        Returns:
            Energy consumed in Joules
        """
        # Minimal energy in idle state
        return 0.001 * self.E_elec

    def sensing_energy(self):
        """
        Calculate energy consumed for sensing operation.

        Returns:
            Energy consumed in Joules
        """
        # Typical sensing energy
        return 10e-9  # 10 nJ per sensing operation

    def compute_max_distance(self, available_energy, num_bits=None):
        """
        Compute maximum transmission distance for given energy budget.

        Args:
            available_energy: Available energy (J)
            num_bits: Number of bits to transmit

        Returns:
            Maximum distance in meters
        """
        if num_bits is None:
            num_bits = self.packet_size

        # Subtract electronics energy
        e_remaining = available_energy - (self.E_elec * num_bits)

        if e_remaining <= 0:
            return 0

        # Calculate distance for free space model
        d_fs = math.sqrt(e_remaining / (self.E_fs * num_bits))

        if d_fs < self.d0:
            return d_fs
        else:
            # Use multi-path model
            d_mp = (e_remaining / (self.E_mp * num_bits)) ** 0.25
            return d_mp


# Default energy model instance
default_energy_model = EnergyModel()
