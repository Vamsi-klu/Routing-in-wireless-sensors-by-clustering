package main

import (
	"fmt"
	"math/rand"
	"time"

	"github.com/wsn-routing/go-wsn/pkg/leach"
	"github.com/wsn-routing/go-wsn/pkg/network"
)

func main() {
	// Seed random number generator
	rand.Seed(time.Now().UnixNano())

	fmt.Println("======================================================================")
	fmt.Println("WIRELESS SENSOR NETWORK SIMULATION - LEACH PROTOCOL (Go Implementation)")
	fmt.Println("======================================================================")

	// Create network
	fmt.Println("\n1. Creating wireless sensor network...")
	net := network.NewNetwork(
		100,          // num_nodes
		100, 100,     // area dimensions
		50, 150,      // base station location
		0.5,          // initial energy per node
		"random",     // deployment strategy
	)
	fmt.Printf("   Created network with %d nodes\n", net.NumNodes)
	fmt.Printf("   Deployment area: %.0fx%.0fm\n", net.AreaWidth, net.AreaHeight)
	fmt.Printf("   Base station at: (%.0f, %.0f)\n", net.BaseStationX, net.BaseStationY)

	// Initialize LEACH
	fmt.Println("\n2. Initializing LEACH protocol...")
	leachProtocol := leach.NewLEACH(net, 0.05, 20)
	fmt.Printf("   Cluster head probability: %.0f%%\n", leachProtocol.P*100)

	// Run simulation
	fmt.Println("\n3. Running simulation...")
	maxRounds := 1000
	printInterval := 100

	for round := 1; round <= maxRounds; round++ {
		// Run one round
		stats := leachProtocol.RunRound()

		// Update network lifetime stats
		net.UpdateLifetimeStats(round)

		// Print progress
		if round%printInterval == 0 {
			fmt.Printf("\n   Round %d:\n", round)
			fmt.Printf("   - Alive nodes: %d/%d\n", stats.AliveNodes, net.NumNodes)
			fmt.Printf("   - Cluster heads: %d\n", stats.NumClusterHeads)
			fmt.Printf("   - Packets to BS: %d\n", stats.PacketsToBS)
			fmt.Printf("   - Avg energy: %.4f J\n", stats.AvgEnergy)
		}

		// Stop if network is dead
		if net.IsDead() {
			fmt.Printf("\n   Network died at round %d\n", round)
			break
		}
	}

	// Print final statistics
	fmt.Println("\n4. Simulation complete!")
	fmt.Println()
	net.PrintStatistics()

	// Print LEACH statistics
	fmt.Println("\n======================================================================")
	fmt.Println("LEACH PROTOCOL STATISTICS")
	fmt.Println("======================================================================")
	stats := leachProtocol.GetStatistics()
	fmt.Printf("Total Rounds: %d\n", stats["total_rounds"])
	fmt.Printf("Alive Nodes: %d\n", stats["alive_nodes"])
	fmt.Printf("Dead Nodes: %d\n", stats["dead_nodes"])
	fmt.Printf("Total Packets to BS: %d\n", stats["total_packets_to_bs"])
	fmt.Printf("Total Energy Consumed: %.6f J\n", stats["total_energy_consumed"])
	fmt.Printf("Avg Packets per Round: %.2f\n", stats["avg_packets_per_round"])
	fmt.Println("======================================================================")
}
