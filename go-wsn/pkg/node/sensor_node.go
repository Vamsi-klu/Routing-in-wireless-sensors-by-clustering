package node

import (
	"fmt"
	"math"

	"github.com/wsn-routing/go-wsn/pkg/energy"
)

// NodeType represents the type/role of a node
type NodeType int

const (
	Normal NodeType = iota
	ClusterHead
	BaseStation
)

// NodeState represents the operational state of a node
type NodeState int

const (
	Active NodeState = iota
	Sleep
	Dead
)

// String returns string representation of NodeType
func (nt NodeType) String() string {
	switch nt {
	case Normal:
		return "normal"
	case ClusterHead:
		return "cluster_head"
	case BaseStation:
		return "base_station"
	default:
		return "unknown"
	}
}

// String returns string representation of NodeState
func (ns NodeState) String() string {
	switch ns {
	case Active:
		return "active"
	case Sleep:
		return "sleep"
	case Dead:
		return "dead"
	default:
		return "unknown"
	}
}

// SensorNode represents a sensor node in a wireless sensor network
type SensorNode struct {
	ID             int
	X              float64
	Y              float64
	InitialEnergy  float64
	Energy         float64
	EnergyModel    *energy.EnergyModel
	NodeType       NodeType
	State          NodeState
	IsClusterHead  bool
	ClusterHead    *SensorNode
	ClusterMembers []*SensorNode
	CHRounds       int
	LastCHRound    int
	Round          int
	PacketsSent    int
	PacketsRecv    int
	TotalTxDist    float64
}

// NewSensorNode creates a new sensor node
func NewSensorNode(id int, x, y, initialEnergy float64, energyModel *energy.EnergyModel) *SensorNode {
	if energyModel == nil {
		energyModel = energy.DefaultEnergyModel
	}

	return &SensorNode{
		ID:             id,
		X:              x,
		Y:              y,
		InitialEnergy:  initialEnergy,
		Energy:         initialEnergy,
		EnergyModel:    energyModel,
		NodeType:       Normal,
		State:          Active,
		IsClusterHead:  false,
		ClusterHead:    nil,
		ClusterMembers: make([]*SensorNode, 0),
		CHRounds:       0,
		LastCHRound:    -1,
		Round:          0,
		PacketsSent:    0,
		PacketsRecv:    0,
		TotalTxDist:    0.0,
	}
}

// DistanceTo calculates Euclidean distance to another node or coordinates
func (n *SensorNode) DistanceTo(targetX, targetY float64) float64 {
	return math.Sqrt(math.Pow(n.X-targetX, 2) + math.Pow(n.Y-targetY, 2))
}

// DistanceToNode calculates distance to another node
func (n *SensorNode) DistanceToNode(other *SensorNode) float64 {
	return n.DistanceTo(other.X, other.Y)
}

// IsAlive checks if node has remaining energy
func (n *SensorNode) IsAlive() bool {
	return n.Energy > 0 && n.State != Dead
}

// IsDead checks if node is dead
func (n *SensorNode) IsDead() bool {
	return n.Energy <= 0 || n.State == Dead
}

// Transmit transmits data to a destination
func (n *SensorNode) Transmit(destX, destY float64, numBits ...int) bool {
	if !n.IsAlive() {
		return false
	}

	distance := n.DistanceTo(destX, destY)
	energyRequired := n.EnergyModel.TransmitEnergy(distance, numBits...)

	if n.Energy >= energyRequired {
		n.Energy -= energyRequired
		n.PacketsSent++
		n.TotalTxDist += distance

		if n.Energy <= 0 {
			n.State = Dead
		}

		return true
	}

	n.State = Dead
	n.Energy = 0
	return false
}

// TransmitToNode transmits data to another node
func (n *SensorNode) TransmitToNode(dest *SensorNode, numBits ...int) bool {
	return n.Transmit(dest.X, dest.Y, numBits...)
}

// Receive receives data
func (n *SensorNode) Receive(numBits ...int) bool {
	if !n.IsAlive() {
		return false
	}

	energyRequired := n.EnergyModel.ReceiveEnergy(numBits...)

	if n.Energy >= energyRequired {
		n.Energy -= energyRequired
		n.PacketsRecv++

		if n.Energy <= 0 {
			n.State = Dead
		}

		return true
	}

	n.State = Dead
	n.Energy = 0
	return false
}

// AggregateData performs data aggregation
func (n *SensorNode) AggregateData(numPackets int) bool {
	if !n.IsAlive() {
		return false
	}

	energyRequired := n.EnergyModel.AggregateEnergy(numPackets)

	if n.Energy >= energyRequired {
		n.Energy -= energyRequired

		if n.Energy <= 0 {
			n.State = Dead
		}

		return true
	}

	n.State = Dead
	n.Energy = 0
	return false
}

// Sense performs sensing operation
func (n *SensorNode) Sense() bool {
	if !n.IsAlive() {
		return false
	}

	energyRequired := n.EnergyModel.SensingEnergy()

	if n.Energy >= energyRequired {
		n.Energy -= energyRequired

		if n.Energy <= 0 {
			n.State = Dead
		}

		return true
	}

	n.State = Dead
	n.Energy = 0
	return false
}

// SetClusterHead sets node as cluster head or normal node
func (n *SensorNode) SetClusterHead(isCH bool) {
	n.IsClusterHead = isCH

	if isCH {
		n.NodeType = ClusterHead
		n.ClusterMembers = make([]*SensorNode, 0)
		n.ClusterHead = n
		n.CHRounds++
		n.LastCHRound = n.Round
	} else {
		n.NodeType = Normal
		n.ClusterMembers = nil
		n.ClusterHead = nil
	}
}

// JoinCluster joins a cluster by associating with a cluster head
func (n *SensorNode) JoinCluster(clusterHead *SensorNode) {
	n.ClusterHead = clusterHead
	n.IsClusterHead = false
	n.NodeType = Normal
}

// GetEnergyPercentage returns remaining energy as percentage
func (n *SensorNode) GetEnergyPercentage() float64 {
	if n.InitialEnergy == 0 {
		return 0
	}
	return (n.Energy / n.InitialEnergy) * 100
}

// ResetForNewRound resets node state for a new round
func (n *SensorNode) ResetForNewRound() {
	n.Round++
	if !n.IsClusterHead {
		n.ClusterHead = nil
		n.ClusterMembers = nil
	}
}

// String returns string representation of the node
func (n *SensorNode) String() string {
	return fmt.Sprintf("Node %d: (%.1f, %.1f), Energy: %.4fJ (%.1f%%), Type: %s, State: %s",
		n.ID, n.X, n.Y, n.Energy, n.GetEnergyPercentage(), n.NodeType, n.State)
}
