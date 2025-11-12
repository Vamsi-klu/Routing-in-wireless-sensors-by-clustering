package energy

import (
	"math"
	"testing"
)

func TestNewEnergyModel(t *testing.T) {
	model := NewEnergyModel()

	if model.EElec != 50e-9 {
		t.Errorf("Expected EElec = 50e-9, got %e", model.EElec)
	}
	if model.D0 != 87.7 {
		t.Errorf("Expected D0 = 87.7, got %f", model.D0)
	}
	if model.PacketSize != 4000 {
		t.Errorf("Expected PacketSize = 4000, got %d", model.PacketSize)
	}
}

func TestTransmitEnergyShortDistance(t *testing.T) {
	model := NewEnergyModel()
	distance := 10.0 // meters, less than d0

	energy := model.TransmitEnergy(distance)

	if energy <= 0 {
		t.Errorf("Energy should be positive, got %f", energy)
	}

	// Check it uses free space model
	expectedElec := model.EElec * float64(model.PacketSize)
	expectedAmp := model.EFS * float64(model.PacketSize) * math.Pow(distance, 2)
	expected := expectedElec + expectedAmp

	if math.Abs(energy-expected) > 1e-15 {
		t.Errorf("Expected energy %e, got %e", expected, energy)
	}
}

func TestTransmitEnergyLongDistance(t *testing.T) {
	model := NewEnergyModel()
	distance := 100.0 // meters, greater than d0

	energy := model.TransmitEnergy(distance)

	if energy <= 0 {
		t.Errorf("Energy should be positive, got %f", energy)
	}

	// Check it uses multi-path model
	expectedElec := model.EElec * float64(model.PacketSize)
	expectedAmp := model.EMP * float64(model.PacketSize) * math.Pow(distance, 4)
	expected := expectedElec + expectedAmp

	if math.Abs(energy-expected) > 1e-15 {
		t.Errorf("Expected energy %e, got %e", expected, energy)
	}
}

func TestReceiveEnergy(t *testing.T) {
	model := NewEnergyModel()
	energy := model.ReceiveEnergy()

	expected := model.EElec * float64(model.PacketSize)

	if math.Abs(energy-expected) > 1e-15 {
		t.Errorf("Expected energy %e, got %e", expected, energy)
	}
}

func TestAggregateEnergy(t *testing.T) {
	model := NewEnergyModel()
	numPackets := 10

	energy := model.AggregateEnergy(numPackets)

	expected := model.EDA * float64(model.PacketSize) * float64(numPackets)

	if math.Abs(energy-expected) > 1e-15 {
		t.Errorf("Expected energy %e, got %e", expected, energy)
	}
}

func TestComputeMaxDistanceShortRange(t *testing.T) {
	model := NewEnergyModel()
	availableEnergy := 0.001 // 1 mJ

	maxDist := model.ComputeMaxDistance(availableEnergy)

	if maxDist <= 0 {
		t.Errorf("Max distance should be positive, got %f", maxDist)
	}

	// Verify it's achievable (allow small tolerance for floating point errors)
	energyNeeded := model.TransmitEnergy(maxDist)
	if energyNeeded > availableEnergy*1.01 { // Allow 1% tolerance
		t.Errorf("Computed distance %f requires significantly more energy than available: needed=%e, available=%e", maxDist, energyNeeded, availableEnergy)
	}
}

func TestComputeMaxDistanceInsufficientEnergy(t *testing.T) {
	model := NewEnergyModel()
	availableEnergy := model.EElec * float64(model.PacketSize) * 0.5

	maxDist := model.ComputeMaxDistance(availableEnergy)

	if maxDist != 0 {
		t.Errorf("Expected max distance = 0 for insufficient energy, got %f", maxDist)
	}
}

func TestEnergyIncreaseWithDistance(t *testing.T) {
	model := NewEnergyModel()

	energy10 := model.TransmitEnergy(10)
	energy20 := model.TransmitEnergy(20)
	energy50 := model.TransmitEnergy(50)

	if energy20 <= energy10 || energy50 <= energy20 {
		t.Errorf("Energy should increase with distance: %e, %e, %e", energy10, energy20, energy50)
	}
}
