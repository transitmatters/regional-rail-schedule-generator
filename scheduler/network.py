from dataclasses import dataclass
from typing import List, Dict, Set, Tuple

from synthesize.time import Timetable
from synthesize.definitions import RoutePattern
from synthesize.util import listify

from scheduler.key_stations import get_key_stations


@dataclass(frozen=True, eq=True)
class Node:
    id: str
    exclusion_time_s: int = 60


@dataclass
class Service:
    id: str
    trips_per_hour: int
    calls_at_nodes: List[Node]
    timetable: Timetable

    def __str__(self):
        return self.id

    @property
    def headway_mins(self):
        return 60 / self.trips_per_hour

    def trip_time_to_node_seconds(self, node: Node):
        first_node = self.calls_at_nodes[0]
        return self.timetable.get_travel_time(first_node, node)


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


# def get_order_determining_station(
#     route_patterns: List[RoutePattern], key_stations: List[str]
# ) -> str:
#     for key_station in key_stations:
#         for route_pattern in route_patterns:
#             if key_station not in route_pattern.station_names:
#                 break
#         else:
#             return key_station


def get_node_timetable(route_pattern: RoutePattern, nodes_by_id: Dict[str, Node]) -> Timetable:
    return route_pattern.timetable.map(lambda key: nodes_by_id.get(key))


def create_scheduler_network(
    route_patterns: List[RoutePattern], trips_per_hour_by_route_pattern: Dict[str, int]
):
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
            trips_per_hour=trips_per_hour_by_route_pattern[route_pattern.id],
            calls_at_nodes=calls_at_nodes,
            timetable=get_node_timetable(route_pattern, nodes_by_id),
        )
        services_by_route_id[route_pattern.id] = service

    return SchedulerNetwork(
        nodes=nodes_by_id,
        edges=edges,
        services=services_by_route_id,
    )
