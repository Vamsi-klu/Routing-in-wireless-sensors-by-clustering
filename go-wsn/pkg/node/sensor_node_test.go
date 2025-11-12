package node

import (
	"testing"

	"github.com/wsn-routing/go-wsn/pkg/energy"
)

func TestNewSensorNode(t *testing.T) {
	node := NewSensorNode(0, 10, 20, 0.5, nil)

	if node.ID != 0 {
		t.Errorf("Expected ID = 0, got %d", node.ID)
	}
	if node.X != 10 || node.Y != 20 {
		t.Errorf("Expected position (10, 20), got (%.1f, %.1f)", node.X, node.Y)
	}
	if node.Energy != 0.5 {
		t.Errorf("Expected energy = 0.5, got %f", node.Energy)
	}
	if node.State != Active {
		t.Errorf("Expected state = Active, got %v", node.State)
	}
}

func TestDistanceCalculation(t *testing.T) {
	node1 := NewSensorNode(0, 0, 0, 0.5, nil)
	node2 := NewSensorNode(1, 3, 4, 0.5, nil)

	distance := node1.DistanceToNode(node2)

	if distance != 5.0 {
		t.Errorf("Expected distance = 5.0, got %f", distance)
	}
}

func TestIsAlive(t *testing.T) {
	node := NewSensorNode(0, 0, 0, 0.5, nil)

	if !node.IsAlive() {
		t.Error("Node should be alive initially")
	}

	node.Energy = 0
	node.State = Dead

	if node.IsAlive() {
		t.Error("Node should be dead with zero energy")
	}
}

func TestTransmit(t *testing.T) {
	model := energy.NewEnergyModel()
	node := NewSensorNode(0, 0, 0, 1.0, model)

	initialEnergy := node.Energy
	success := node.Transmit(10, 0)

	if !success {
		t.Error("Transmission should succeed")
	}
	if node.Energy >= initialEnergy {
		t.Error("Energy should decrease after transmission")
	}
	if node.PacketsSent != 1 {
		t.Errorf("Expected packets_sent = 1, got %d", node.PacketsSent)
	}
}

func TestTransmitInsufficientEnergy(t *testing.T) {
	node := NewSensorNode(0, 0, 0, 0.00001, nil)

	success := node.Transmit(100, 100) // Far away

	if success {
		t.Error("Transmission should fail with insufficient energy")
	}
	if node.State != Dead {
		t.Error("Node should be dead after failed transmission")
	}
}

func TestReceive(t *testing.T) {
	node := NewSensorNode(0, 0, 0, 1.0, nil)

	initialEnergy := node.Energy
	success := node.Receive()

	if !success {
		t.Error("Reception should succeed")
	}
	if node.Energy >= initialEnergy {
		t.Error("Energy should decrease after reception")
	}
	if node.PacketsRecv != 1 {
		t.Errorf("Expected packets_recv = 1, got %d", node.PacketsRecv)
	}
}

func TestAggregateData(t *testing.T) {
	node := NewSensorNode(0, 0, 0, 1.0, nil)

	initialEnergy := node.Energy
	success := node.AggregateData(5)

	if !success {
		t.Error("Aggregation should succeed")
	}
	if node.Energy >= initialEnergy {
		t.Error("Energy should decrease after aggregation")
	}
}

func TestSetClusterHead(t *testing.T) {
	node := NewSensorNode(0, 0, 0, 0.5, nil)
	node.Round = 5

	node.SetClusterHead(true)

	if !node.IsClusterHead {
		t.Error("Node should be cluster head")
	}
	if node.NodeType != ClusterHead {
		t.Error("Node type should be ClusterHead")
	}
	if node.CHRounds != 1 {
		t.Errorf("Expected CHRounds = 1, got %d", node.CHRounds)
	}
	if node.LastCHRound != 5 {
		t.Errorf("Expected LastCHRound = 5, got %d", node.LastCHRound)
	}
}

func TestGetEnergyPercentage(t *testing.T) {
	node := NewSensorNode(0, 0, 0, 1.0, nil)

	percentage := node.GetEnergyPercentage()
	if percentage != 100.0 {
		t.Errorf("Expected 100%%, got %.1f%%", percentage)
	}

	node.Energy = 0.5
	percentage = node.GetEnergyPercentage()
	if percentage != 50.0 {
		t.Errorf("Expected 50%%, got %.1f%%", percentage)
	}
}
