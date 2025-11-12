package energy

import (
	"math"
)

// EnergyModel represents the first-order radio energy model for WSN
// Based on the energy dissipation model from LEACH paper
type EnergyModel struct {
	EElec      float64 // Energy to run transmitter/receiver circuit (J/bit)
	EFS        float64 // Free space amplifier energy (J/bit/m^2)
	EMP        float64 // Multi-path amplifier energy (J/bit/m^4)
	EDA        float64 // Data aggregation energy (J/bit/signal)
	D0         float64 // Crossover distance (m)
	PacketSize int     // Default packet size (bits)
}

// NewEnergyModel creates a new energy model with default parameters
func NewEnergyModel() *EnergyModel {
	return &EnergyModel{
		EElec:      50e-9,      // 50 nJ/bit
		EFS:        10e-12,     // 10 pJ/bit/m^2
		EMP:        0.0013e-12, // 0.0013 pJ/bit/m^4
		EDA:        5e-9,       // 5 nJ/bit/signal
		D0:         87.7,       // 87.7 meters
		PacketSize: 4000,       // 4000 bits
	}
}

// NewCustomEnergyModel creates an energy model with custom parameters
func NewCustomEnergyModel(eElec, eFS, eMP, eDA, d0 float64, packetSize int) *EnergyModel {
	return &EnergyModel{
		EElec:      eElec,
		EFS:        eFS,
		EMP:        eMP,
		EDA:        eDA,
		D0:         d0,
		PacketSize: packetSize,
	}
}

// TransmitEnergy calculates energy consumed for transmitting data
// Uses free space model (d^2) for short distances and
// multi-path model (d^4) for long distances
func (em *EnergyModel) TransmitEnergy(distance float64, numBits ...int) float64 {
	bits := em.PacketSize
	if len(numBits) > 0 {
		bits = numBits[0]
	}

	// Electronics energy
	eElec := em.EElec * float64(bits)

	// Amplification energy (depends on distance)
	var eAmp float64
	if distance < em.D0 {
		// Free space model (d^2)
		eAmp = em.EFS * float64(bits) * math.Pow(distance, 2)
	} else {
		// Multi-path fading model (d^4)
		eAmp = em.EMP * float64(bits) * math.Pow(distance, 4)
	}

	return eElec + eAmp
}

// ReceiveEnergy calculates energy consumed for receiving data
func (em *EnergyModel) ReceiveEnergy(numBits ...int) float64 {
	bits := em.PacketSize
	if len(numBits) > 0 {
		bits = numBits[0]
	}

	return em.EElec * float64(bits)
}

// AggregateEnergy calculates energy consumed for data aggregation
func (em *EnergyModel) AggregateEnergy(numPackets int) float64 {
	return em.EDA * float64(em.PacketSize) * float64(numPackets)
}

// IdleEnergy calculates energy consumed in idle state per time unit
func (em *EnergyModel) IdleEnergy() float64 {
	return 0.001 * em.EElec
}

// SensingEnergy calculates energy consumed for sensing operation
func (em *EnergyModel) SensingEnergy() float64 {
	return 10e-9 // 10 nJ per sensing operation
}

// ComputeMaxDistance computes maximum transmission distance for given energy budget
func (em *EnergyModel) ComputeMaxDistance(availableEnergy float64, numBits ...int) float64 {
	bits := em.PacketSize
	if len(numBits) > 0 {
		bits = numBits[0]
	}

	// Subtract electronics energy
	eRemaining := availableEnergy - (em.EElec * float64(bits))

	if eRemaining <= 0 {
		return 0
	}

	// Calculate distance for free space model
	dFS := math.Sqrt(eRemaining / (em.EFS * float64(bits)))

	if dFS < em.D0 {
		return dFS
	}

	// Use multi-path model
	dMP := math.Pow(eRemaining/(em.EMP*float64(bits)), 0.25)
	return dMP
}

// DefaultEnergyModel is the default instance
var DefaultEnergyModel = NewEnergyModel()
