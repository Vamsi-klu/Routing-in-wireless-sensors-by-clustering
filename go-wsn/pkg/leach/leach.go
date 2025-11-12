package leach

import (
	"fmt"
	"math"
	"math/rand"

	"github.com/wsn-routing/go-wsn/pkg/network"
	"github.com/wsn-routing/go-wsn/pkg/node"
)

// LEACH represents the LEACH clustering protocol
type LEACH struct {
	Network              *network.WirelessSensorNetwork
	P                    float64 // Cluster head probability
	RoundTime            int
	CurrentRound         int
	ClusterHeads         []*node.SensorNode
	Clusters             map[int][]*node.SensorNode
	TotalPacketsToBS     int
	TotalEnergyConsumed  float64
	RoundsHistory        []RoundStats
}

// RoundStats stores statistics for a round
type RoundStats struct {
	Round           int
	NumClusterHeads int
	PacketsToBS     int
	EnergyConsumed  float64
	AliveNodes      int
	TotalEnergy     float64
	AvgEnergy       float64
}

// NewLEACH creates a new LEACH protocol instance
func NewLEACH(net *network.WirelessSensorNetwork, chProbability float64, roundTime int) *LEACH {
	return &LEACH{
		Network:             net,
		P:                   chProbability,
		RoundTime:           roundTime,
		CurrentRound:        0,
		ClusterHeads:        make([]*node.SensorNode, 0),
		Clusters:            make(map[int][]*node.SensorNode),
		TotalPacketsToBS:    0,
		TotalEnergyConsumed: 0.0,
		RoundsHistory:       make([]RoundStats, 0),
	}
}

// RunRound executes one complete round of LEACH protocol
func (l *LEACH) RunRound() RoundStats {
	l.CurrentRound++

	// Setup phase
	l.SetupPhase()

	// Steady-state phase
	stats := l.SteadyStatePhase()

	// Record statistics
	l.RoundsHistory = append(l.RoundsHistory, stats)

	return stats
}

// SetupPhase performs setup phase: CH election and cluster formation
func (l *LEACH) SetupPhase() {
	// Reset previous round clustering
	l.ClusterHeads = make([]*node.SensorNode, 0)
	l.Clusters = make(map[int][]*node.SensorNode)

	// Step 1: Cluster Head Election
	l.electClusterHeads()

	// Step 2: Cluster Formation
	if len(l.ClusterHeads) > 0 {
		l.formClusters()
	} else {
		// If no CHs elected, force election
		l.forceClusterHeadElection()
		if len(l.ClusterHeads) > 0 {
			l.formClusters()
		}
	}
}

// electClusterHeads elects cluster heads based on LEACH threshold function
func (l *LEACH) electClusterHeads() {
	aliveNodes := l.Network.GetAliveNodes()

	if len(aliveNodes) == 0 {
		return
	}

	// Calculate rotation period
	rotationPeriod := 1
	if l.P > 0 {
		rotationPeriod = int(1 / l.P)
	}

	for _, n := range aliveNodes {
		// Check if node was CH recently
		roundsSinceCH := l.CurrentRound - n.LastCHRound

		// Node is eligible if it wasn't CH in last rotation period
		if roundsSinceCH >= rotationPeriod || n.LastCHRound < 0 {
			// Calculate threshold
			rMod := l.CurrentRound % rotationPeriod
			threshold := l.P
			if rMod != 0 {
				threshold = l.P / (1 - l.P*float64(rMod))
			}

			// Add energy-based adjustment
			energyFactor := n.Energy / n.InitialEnergy
			adjustedThreshold := threshold * energyFactor

			// Random selection based on threshold
			if rand.Float64() < adjustedThreshold {
				n.SetClusterHead(true)
				l.ClusterHeads = append(l.ClusterHeads, n)
				l.Clusters[n.ID] = make([]*node.SensorNode, 0)
			} else {
				n.SetClusterHead(false)
			}
		} else {
			n.SetClusterHead(false)
		}
	}
}

// forceClusterHeadElection forces at least one cluster head election
func (l *LEACH) forceClusterHeadElection() {
	aliveNodes := l.Network.GetAliveNodes()

	if len(aliveNodes) == 0 {
		return
	}

	// Select node with maximum energy
	var bestNode *node.SensorNode
	maxEnergy := 0.0

	for _, n := range aliveNodes {
		if n.Energy > maxEnergy {
			maxEnergy = n.Energy
			bestNode = n
		}
	}

	if bestNode != nil {
		bestNode.SetClusterHead(true)
		l.ClusterHeads = append(l.ClusterHeads, bestNode)
		l.Clusters[bestNode.ID] = make([]*node.SensorNode, 0)
	}
}

// formClusters forms clusters by having non-CH nodes join nearest CH
func (l *LEACH) formClusters() {
	if len(l.ClusterHeads) == 0 {
		return
	}

	// Non-CH nodes join nearest cluster head
	for _, n := range l.Network.Nodes {
		if n.IsAlive() && !n.IsClusterHead {
			// Find nearest cluster head
			var nearestCH *node.SensorNode
			minDist := math.MaxFloat64

			for _, ch := range l.ClusterHeads {
				dist := n.DistanceToNode(ch)
				if dist < minDist {
					minDist = dist
					nearestCH = ch
				}
			}

			// Join cluster
			if nearestCH != nil {
				n.JoinCluster(nearestCH)
				l.Clusters[nearestCH.ID] = append(l.Clusters[nearestCH.ID], n)

				// Energy cost for receiving CH advertisement and sending join request
				n.Receive()                  // Receive CH advertisement
				n.TransmitToNode(nearestCH)  // Send join request
				nearestCH.Receive()          // CH receives join request
			}
		}
	}
}

// SteadyStatePhase performs steady-state phase: data collection and transmission
func (l *LEACH) SteadyStatePhase() RoundStats {
	packetsToBS := 0
	energyStart := 0.0
	for _, n := range l.Network.Nodes {
		energyStart += n.Energy
	}

	// Process each cluster
	for _, ch := range l.ClusterHeads {
		if !ch.IsAlive() {
			continue
		}

		clusterMembers := l.Clusters[ch.ID]
		aliveMembers := make([]*node.SensorNode, 0)

		for _, member := range clusterMembers {
			if member.IsAlive() {
				aliveMembers = append(aliveMembers, member)
			}
		}

		// Step 1: Members send data to CH
		for _, member := range aliveMembers {
			member.Sense()             // Sense data
			member.TransmitToNode(ch)  // Send to CH
			ch.Receive()               // CH receives
		}

		// Step 2: CH aggregates data
		if len(aliveMembers) > 0 {
			ch.AggregateData(len(aliveMembers))
		}

		// Step 3: CH sends aggregated data to base station
		if ch.Transmit(l.Network.BaseStationX, l.Network.BaseStationY) {
			packetsToBS++
		}
	}

	// Update statistics
	l.TotalPacketsToBS += packetsToBS

	energyEnd := 0.0
	for _, n := range l.Network.Nodes {
		energyEnd += n.Energy
	}
	energyConsumed := energyStart - energyEnd
	l.TotalEnergyConsumed += energyConsumed

	// Collect statistics
	aliveNodes := l.Network.GetAliveNodes()
	totalEnergy := 0.0
	for _, n := range l.Network.Nodes {
		totalEnergy += n.Energy
	}

	avgEnergy := 0.0
	if len(l.Network.Nodes) > 0 {
		avgEnergy = totalEnergy / float64(len(l.Network.Nodes))
	}

	return RoundStats{
		Round:           l.CurrentRound,
		NumClusterHeads: len(l.ClusterHeads),
		PacketsToBS:     packetsToBS,
		EnergyConsumed:  energyConsumed,
		AliveNodes:      len(aliveNodes),
		TotalEnergy:     totalEnergy,
		AvgEnergy:       avgEnergy,
	}
}

// GetStatistics returns protocol statistics
func (l *LEACH) GetStatistics() map[string]interface{} {
	aliveNodes := l.Network.GetAliveNodes()
	deadNodes := l.Network.GetDeadNodes()

	avgPacketsPerRound := 0.0
	if l.CurrentRound > 0 {
		avgPacketsPerRound = float64(l.TotalPacketsToBS) / float64(l.CurrentRound)
	}

	return map[string]interface{}{
		"total_rounds":         l.CurrentRound,
		"alive_nodes":          len(aliveNodes),
		"dead_nodes":           len(deadNodes),
		"total_packets_to_bs":  l.TotalPacketsToBS,
		"total_energy_consumed": l.TotalEnergyConsumed,
		"avg_packets_per_round": avgPacketsPerRound,
		"current_cluster_heads": len(l.ClusterHeads),
	}
}

// PrintRoundInfo prints information about current round
func (l *LEACH) PrintRoundInfo() {
	stats := l.GetStatistics()

	fmt.Printf("\n=== Round %d ===\n", l.CurrentRound)
	fmt.Printf("Cluster Heads: %d\n", len(l.ClusterHeads))
	fmt.Printf("Alive Nodes: %d/%d\n", stats["alive_nodes"], l.Network.NumNodes)
	fmt.Printf("Packets to BS: %d\n", l.TotalPacketsToBS)
	fmt.Printf("Total Energy Consumed: %.6f J\n", l.TotalEnergyConsumed)
}
