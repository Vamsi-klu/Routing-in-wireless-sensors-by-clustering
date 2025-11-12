package network

import (
	"fmt"
	"math"
	"math/rand"

	"github.com/wsn-routing/go-wsn/pkg/energy"
	"github.com/wsn-routing/go-wsn/pkg/node"
)

// WirelessSensorNetwork represents a WSN simulation environment
type WirelessSensorNetwork struct {
	NumNodes              int
	AreaWidth             float64
	AreaHeight            float64
	BaseStationX          float64
	BaseStationY          float64
	InitialEnergy         float64
	EnergyModel           *energy.EnergyModel
	Deployment            string
	Nodes                 []*node.SensorNode
	CurrentRound          int
	FirstNodeDeathRound   *int
	HalfNodesDeathRound   *int
	LastNodeDeathRound    *int
}

// NewNetwork creates a new wireless sensor network
func NewNetwork(numNodes int, areaWidth, areaHeight float64, baseStationX, baseStationY, initialEnergy float64, deployment string) *WirelessSensorNetwork {
	network := &WirelessSensorNetwork{
		NumNodes:       numNodes,
		AreaWidth:      areaWidth,
		AreaHeight:     areaHeight,
		BaseStationX:   baseStationX,
		BaseStationY:   baseStationY,
		InitialEnergy:  initialEnergy,
		EnergyModel:    energy.DefaultEnergyModel,
		Deployment:     deployment,
		Nodes:          make([]*node.SensorNode, 0, numNodes),
		CurrentRound:   0,
	}

	network.deployNodes()
	return network
}

// deployNodes deploys sensor nodes in the network area
func (nw *WirelessSensorNetwork) deployNodes() {
	switch nw.Deployment {
	case "random":
		nw.randomDeployment()
	case "grid":
		nw.gridDeployment()
	case "cluster":
		nw.clusterDeployment()
	default:
		nw.randomDeployment()
	}
}

// randomDeployment randomly deploys nodes in the area
func (nw *WirelessSensorNetwork) randomDeployment() {
	for i := 0; i < nw.NumNodes; i++ {
		x := rand.Float64() * nw.AreaWidth
		y := rand.Float64() * nw.AreaHeight
		n := node.NewSensorNode(i, x, y, nw.InitialEnergy, nw.EnergyModel)
		nw.Nodes = append(nw.Nodes, n)
	}
}

// gridDeployment deploys nodes in a grid pattern
func (nw *WirelessSensorNetwork) gridDeployment() {
	gridSize := int(math.Ceil(math.Sqrt(float64(nw.NumNodes))))
	xStep := nw.AreaWidth / float64(gridSize+1)
	yStep := nw.AreaHeight / float64(gridSize+1)

	nodeID := 0
	for i := 0; i < gridSize; i++ {
		for j := 0; j < gridSize; j++ {
			if nodeID >= nw.NumNodes {
				break
			}
			x := float64(i+1) * xStep
			y := float64(j+1) * yStep
			n := node.NewSensorNode(nodeID, x, y, nw.InitialEnergy, nw.EnergyModel)
			nw.Nodes = append(nw.Nodes, n)
			nodeID++
		}
	}
}

// clusterDeployment deploys nodes in clustered pattern
func (nw *WirelessSensorNetwork) clusterDeployment() {
	numClusters := int(math.Max(3, float64(nw.NumNodes)/20))
	nodesPerCluster := nw.NumNodes / numClusters

	// Generate cluster centers
	centers := make([][2]float64, numClusters)
	for i := 0; i < numClusters; i++ {
		centers[i] = [2]float64{
			0.2*nw.AreaWidth + rand.Float64()*0.6*nw.AreaWidth,
			0.2*nw.AreaHeight + rand.Float64()*0.6*nw.AreaHeight,
		}
	}

	nodeID := 0
	for _, center := range centers {
		for j := 0; j < nodesPerCluster && nodeID < nw.NumNodes; j++ {
			x := math.Max(0, math.Min(nw.AreaWidth, center[0]+rand.NormFloat64()*10))
			y := math.Max(0, math.Min(nw.AreaHeight, center[1]+rand.NormFloat64()*10))
			n := node.NewSensorNode(nodeID, x, y, nw.InitialEnergy, nw.EnergyModel)
			nw.Nodes = append(nw.Nodes, n)
			nodeID++
		}
	}
}

// GetAliveNodes returns list of alive nodes
func (nw *WirelessSensorNetwork) GetAliveNodes() []*node.SensorNode {
	alive := make([]*node.SensorNode, 0)
	for _, n := range nw.Nodes {
		if n.IsAlive() {
			alive = append(alive, n)
		}
	}
	return alive
}

// GetDeadNodes returns list of dead nodes
func (nw *WirelessSensorNetwork) GetDeadNodes() []*node.SensorNode {
	dead := make([]*node.SensorNode, 0)
	for _, n := range nw.Nodes {
		if n.IsDead() {
			dead = append(dead, n)
		}
	}
	return dead
}

// IsDead checks if entire network is dead
func (nw *WirelessSensorNetwork) IsDead() bool {
	for _, n := range nw.Nodes {
		if n.IsAlive() {
			return false
		}
	}
	return true
}

// UpdateLifetimeStats updates network lifetime statistics
func (nw *WirelessSensorNetwork) UpdateLifetimeStats(currentRound int) {
	deadCount := len(nw.GetDeadNodes())

	// First Node Death (FND)
	if nw.FirstNodeDeathRound == nil && deadCount > 0 {
		fnd := currentRound
		nw.FirstNodeDeathRound = &fnd
	}

	// Half Nodes Death (HND)
	if nw.HalfNodesDeathRound == nil && deadCount >= nw.NumNodes/2 {
		hnd := currentRound
		nw.HalfNodesDeathRound = &hnd
	}

	// Last Node Death (LND)
	if nw.LastNodeDeathRound == nil && deadCount == nw.NumNodes {
		lnd := currentRound
		nw.LastNodeDeathRound = &lnd
	}
}

// GetEnergyStatistics calculates energy-related statistics
func (nw *WirelessSensorNetwork) GetEnergyStatistics() map[string]float64 {
	aliveNodes := nw.GetAliveNodes()

	if len(aliveNodes) == 0 {
		totalInitial := float64(nw.NumNodes) * nw.InitialEnergy
		return map[string]float64{
			"total_energy":            0,
			"avg_energy":              0,
			"min_energy":              0,
			"max_energy":              0,
			"total_consumed":          totalInitial,
			"avg_consumed_percentage": 100.0,
		}
	}

	var totalEnergy, minEnergy, maxEnergy float64
	minEnergy = math.MaxFloat64

	for _, n := range aliveNodes {
		totalEnergy += n.Energy
		if n.Energy < minEnergy {
			minEnergy = n.Energy
		}
		if n.Energy > maxEnergy {
			maxEnergy = n.Energy
		}
	}

	totalInitial := float64(nw.NumNodes) * nw.InitialEnergy
	totalCurrent := 0.0
	for _, n := range nw.Nodes {
		totalCurrent += n.Energy
	}
	totalConsumed := totalInitial - totalCurrent

	return map[string]float64{
		"total_energy":            totalCurrent,
		"avg_energy":              totalEnergy / float64(len(aliveNodes)),
		"min_energy":              minEnergy,
		"max_energy":              maxEnergy,
		"total_consumed":          totalConsumed,
		"avg_consumed_percentage": (totalConsumed / totalInitial) * 100,
	}
}

// Reset resets network to initial state
func (nw *WirelessSensorNetwork) Reset() {
	for _, n := range nw.Nodes {
		n.Energy = n.InitialEnergy
		n.State = node.Active
		n.NodeType = node.Normal
		n.PacketsSent = 0
		n.PacketsRecv = 0
		n.IsClusterHead = false
		n.ClusterHead = nil
		n.ClusterMembers = nil
		n.CHRounds = 0
		n.LastCHRound = -1
		n.Round = 0
	}

	nw.CurrentRound = 0
	nw.FirstNodeDeathRound = nil
	nw.HalfNodesDeathRound = nil
	nw.LastNodeDeathRound = nil
}

// PrintStatistics prints network statistics
func (nw *WirelessSensorNetwork) PrintStatistics() {
	aliveNodes := nw.GetAliveNodes()
	deadNodes := nw.GetDeadNodes()
	energyStats := nw.GetEnergyStatistics()

	fmt.Println("============================================================")
	fmt.Println("NETWORK STATISTICS")
	fmt.Println("============================================================")
	fmt.Printf("Total Nodes: %d\n", nw.NumNodes)
	fmt.Printf("Alive Nodes: %d (%.1f%%)\n", len(aliveNodes), float64(len(aliveNodes))/float64(nw.NumNodes)*100)
	fmt.Printf("Dead Nodes: %d\n", len(deadNodes))
	fmt.Println("\nEnergy Statistics:")
	fmt.Printf("  Total Remaining: %.4f J\n", energyStats["total_energy"])
	fmt.Printf("  Average: %.4f J\n", energyStats["avg_energy"])
	fmt.Printf("  Min: %.4f J\n", energyStats["min_energy"])
	fmt.Printf("  Max: %.4f J\n", energyStats["max_energy"])
	fmt.Printf("  Consumed: %.1f%%\n", energyStats["avg_consumed_percentage"])
	fmt.Println("\nNetwork Lifetime:")
	if nw.FirstNodeDeathRound != nil {
		fmt.Printf("  First Node Death: Round %d\n", *nw.FirstNodeDeathRound)
	}
	if nw.HalfNodesDeathRound != nil {
		fmt.Printf("  Half Nodes Death: Round %d\n", *nw.HalfNodesDeathRound)
	}
	if nw.LastNodeDeathRound != nil {
		fmt.Printf("  Last Node Death: Round %d\n", *nw.LastNodeDeathRound)
	}
	fmt.Println("============================================================")
}

// String returns string representation of network
func (nw *WirelessSensorNetwork) String() string {
	alive := len(nw.GetAliveNodes())
	return fmt.Sprintf("WSN: %d/%d nodes alive, Area: %.0fx%.0fm", alive, nw.NumNodes, nw.AreaWidth, nw.AreaHeight)
}
