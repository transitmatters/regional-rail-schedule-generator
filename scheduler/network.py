from dataclasses import dataclass
from typing import List, Dict, Set, Tuple

from synthesize.time import Timetable
from synthesize.definitions import RoutePattern
from synthesize.util import listify

from scheduler.key_stations import get_key_stations


@dataclass(frozen=True, eq=True)
class Node:
    id: str

    def __repr__(self):
        return f"Node({self.id})"


@dataclass
class Service:
    id: str
    calls_at_nodes: List[Node]
    timetable: Timetable

    def trip_time_to_node_seconds(self, node: Node):
        first_node = self.calls_at_nodes[0]
        return self.timetable.get_travel_time(first_node, node)

    def reverse(self):
        return Service(
            id=self.id, calls_at_nodes=list(reversed(self.calls_at_nodes)), timetable=self.timetable
        )

    def __repr__(self):
        return f"Service({self.id})"


@dataclass
class SchedulerNetwork:
    nodes: Dict[str, Node]
    services: Dict[str, Service]
    edges: Set[Tuple[Node, Node]]

    @listify
    def get_services_for_node(self, node: Node):
        for service in self.services.values():
            if node in service.calls_at_nodes:
                yield service

    def reverse(self):
        reversed_services = {k: s.reverse() for (k, s) in self.services.items()}
        reversed_edges = {(b, a) for (a, b) in self.edges}
        return SchedulerNetwork(nodes=self.nodes, services=reversed_services, edges=reversed_edges)


def get_node_timetable(route_pattern: RoutePattern, nodes_by_id: Dict[str, Node]) -> Timetable:
    return route_pattern.timetable.map(lambda key: nodes_by_id.get(key))


def create_scheduler_network(route_patterns: List[RoutePattern]):
    key_stations = get_key_stations(route_patterns)
    nodes_by_id = {}
    services_by_route_id = {}
    edges = set()

    def get_scheduler_graph_node_by_id(node_id: str):
        existing_node = nodes_by_id.get(node_id)
        if existing_node:
            return existing_node
        new_node = Node(id=node_id)
        nodes_by_id[node_id] = new_node
        return new_node

    for route_pattern in route_patterns:
        calls_at_nodes = []
        previous_node = None
        for station_name in route_pattern.station_names:
            if station_name in key_stations:
                station_node = get_scheduler_graph_node_by_id(station_name)
                calls_at_nodes.append(station_node)
                if previous_node:
                    edges.add((previous_node, station_node))
                previous_node = station_node

        service = Service(
            id=route_pattern.id,
            calls_at_nodes=calls_at_nodes,
            timetable=get_node_timetable(route_pattern, nodes_by_id),
        )
        services_by_route_id[route_pattern.id] = service

    return SchedulerNetwork(
        nodes=nodes_by_id,
        edges=edges,
        services=services_by_route_id,
    )
