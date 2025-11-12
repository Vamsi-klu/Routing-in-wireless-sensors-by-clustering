"""
Routing Mechanisms for Wireless Sensor Networks

Implements various routing strategies including direct transmission,
multi-hop routing, and cluster-based routing.
"""

import heapq
from collections import defaultdict


class Router:
    """Base router class for WSN routing protocols"""

    def __init__(self, network):
        """
        Initialize router.

        Args:
            network: WirelessSensorNetwork instance
        """
        self.network = network

    def route_packet(self, source, destination):
        """
        Route a packet from source to destination.

        Args:
            source: Source node
            destination: Destination node or coordinates

        Returns:
            List of nodes in the routing path
        """
        raise NotImplementedError("Subclasses must implement route_packet")


class DirectTransmissionRouter(Router):
    """
    Direct transmission routing - all nodes send directly to base station.
    Simple but energy-inefficient for distant nodes.
    """

    def route_packet(self, source, destination):
        """Direct transmission to destination"""
        return [source, destination]

    def transmit(self, source, destination):
        """Transmit packet directly"""
        return source.transmit(destination)


class MultiHopRouter(Router):
    """
    Multi-hop routing using shortest path based on energy cost.
    Uses Dijkstra's algorithm to find energy-efficient paths.
    """

    def __init__(self, network, max_hop_distance=30):
        """
        Initialize multi-hop router.

        Args:
            network: WirelessSensorNetwork instance
            max_hop_distance: Maximum distance for single hop (meters)
        """
        super().__init__(network)
        self.max_hop_distance = max_hop_distance

    def find_neighbors(self, node, max_distance=None):
        """
        Find neighboring nodes within communication range.

        Args:
            node: Source node
            max_distance: Maximum distance (default: self.max_hop_distance)

        Returns:
            List of neighbor nodes
        """
        if max_distance is None:
            max_distance = self.max_hop_distance

        neighbors = []
        for other in self.network.nodes:
            if other.id != node.id and other.is_alive():
                distance = node.distance_to(other)
                if distance <= max_distance:
                    neighbors.append(other)

        return neighbors

    def find_shortest_path(self, source, destination):
        """
        Find shortest path using Dijkstra's algorithm based on energy cost.

        Args:
            source: Source node
            destination: Destination node or (x, y) tuple

        Returns:
            List of nodes forming the path, or None if no path exists
        """
        # Priority queue: (cost, counter, current_node, path)
        # Counter breaks ties when costs are equal
        counter = 0
        pq = [(0, counter, source, [source])]
        visited = set()
        min_cost = {source.id: 0}

        dest_x, dest_y = destination if isinstance(destination, tuple) else (destination.x, destination.y)

        while pq:
            cost, _, current, path = heapq.heappop(pq)

            if current.id in visited:
                continue

            visited.add(current.id)

            # Check if reached destination
            current_dist_to_dest = ((current.x - dest_x)**2 + (current.y - dest_y)**2)**0.5
            if current_dist_to_dest < self.max_hop_distance:
                return path + [destination] if not isinstance(destination, tuple) else path

            # Explore neighbors
            neighbors = self.find_neighbors(current)

            for neighbor in neighbors:
                if neighbor.id not in visited:
                    # Energy cost for transmission
                    distance = current.distance_to(neighbor)
                    edge_cost = self.network.energy_model.transmit_energy(distance)

                    # Heuristic: prefer nodes with more energy
                    energy_penalty = (1.0 - neighbor.energy / neighbor.initial_energy) * edge_cost

                    total_cost = cost + edge_cost + energy_penalty

                    if neighbor.id not in min_cost or total_cost < min_cost[neighbor.id]:
                        min_cost[neighbor.id] = total_cost
                        counter += 1
                        heapq.heappush(pq, (total_cost, counter, neighbor, path + [neighbor]))

        return None  # No path found

    def route_packet(self, source, destination):
        """Find and return routing path"""
        return self.find_shortest_path(source, destination)

    def transmit(self, source, destination):
        """
        Transmit packet along multi-hop path.

        Args:
            source: Source node
            destination: Destination node or coordinates

        Returns:
            True if successful, False otherwise
        """
        path = self.find_shortest_path(source, destination)

        if not path:
            return False

        # Transmit along path
        for i in range(len(path) - 1):
            current = path[i]
            next_node = path[i + 1]

            if not current.transmit(next_node):
                return False  # Transmission failed

            if isinstance(next_node, tuple):
                # Reached destination coordinates
                return True
            elif not next_node.receive():
                return False  # Reception failed

        return True


class ClusterBasedRouter(Router):
    """
    Cluster-based routing for hierarchical protocols like LEACH.
    Routes data through cluster heads to base station.
    """

    def __init__(self, network):
        super().__init__(network)

    def route_to_cluster_head(self, source):
        """
        Route from source to its cluster head.

        Args:
            source: Source node

        Returns:
            True if successful, False otherwise
        """
        if not source.cluster_head:
            return False

        # Member to CH
        if source.transmit(source.cluster_head):
            return source.cluster_head.receive()

        return False

    def route_to_base_station(self, cluster_head, base_station):
        """
        Route from cluster head to base station.

        Args:
            cluster_head: Cluster head node
            base_station: Base station coordinates

        Returns:
            True if successful, False otherwise
        """
        return cluster_head.transmit(base_station)

    def route_packet(self, source, destination):
        """
        Route packet in cluster-based network.

        Args:
            source: Source node
            destination: Destination (typically base station)

        Returns:
            Routing path [source, CH, destination]
        """
        if source.is_cluster_head:
            return [source, destination]
        elif source.cluster_head:
            return [source, source.cluster_head, destination]
        else:
            # No cluster assigned - direct transmission
            return [source, destination]


class AdaptiveRouter(Router):
    """
    Adaptive router that chooses between direct and multi-hop
    based on distance and energy availability.
    """

    def __init__(self, network, distance_threshold=50):
        """
        Initialize adaptive router.

        Args:
            network: WirelessSensorNetwork instance
            distance_threshold: Distance threshold for choosing routing strategy
        """
        super().__init__(network)
        self.distance_threshold = distance_threshold
        self.direct_router = DirectTransmissionRouter(network)
        self.multihop_router = MultiHopRouter(network)

    def route_packet(self, source, destination):
        """
        Adaptively choose routing strategy.

        Args:
            source: Source node
            destination: Destination node or coordinates

        Returns:
            Routing path
        """
        distance = source.distance_to(destination)

        # Use direct transmission for short distances or high energy
        if distance < self.distance_threshold or source.energy > 0.8 * source.initial_energy:
            return self.direct_router.route_packet(source, destination)
        else:
            # Try multi-hop for energy efficiency
            path = self.multihop_router.route_packet(source, destination)
            if path:
                return path
            else:
                # Fall back to direct transmission
                return self.direct_router.route_packet(source, destination)

    def transmit(self, source, destination):
        """Transmit using adaptive strategy"""
        path = self.route_packet(source, destination)

        if len(path) == 2:
            # Direct transmission
            return self.direct_router.transmit(source, destination)
        else:
            # Multi-hop transmission
            return self.multihop_router.transmit(source, destination)
