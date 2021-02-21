from dataclasses import dataclass
from typing import List, Dict

from synthesize.time import Timetable
from synthesize.definitions import RoutePattern
from synthesize.util import get_triples


@dataclass(eq=True, frozen=True)
class Node:
    station_name: str
    exclusion_time: int = 60


@dataclass
class Service:
    id: str
    trips_per_hour: int
    calls_at_nodes: List[Node]
    timetable: Timetable

    def __str__(self):
        return self.id

    @property
    def headway_seconds(self):
        return 3600 / self.trips_per_hour

    def trip_time_to_node_seconds(self, node: Node):
        first_node = self.calls_at_nodes[0]
        return self.timetable.get_travel_time(first_node, node)


@dataclass
class SchedulerNetwork:
    nodes: Dict[str, Node]
    services: Dict[str, Service]
    order_determining_node: Node

    def get_services_for_node(self, node: Node, ordering=None):
        if ordering is None:
            ordering = self.services.values()
        for service in ordering:
            if node in service.calls_at_nodes:
                yield service


def get_key_stations(route_patterns: List[RoutePattern]):
    adjacent_stations_by_name = {}
    junction_numbers_by_name = {}
    all_station_names = set()
    key_station_names = set()
    for route_pattern in route_patterns:
        stations = route_pattern.station_names
        for station_name in stations:
            all_station_names.add(station_name)
            if not adjacent_stations_by_name.get(station_name):
                adjacent_stations_by_name[station_name] = set()
        for station_before, station_name, station_after in get_triples(stations):
            adjacent_stations_by_name[station_name] |= {station_before, station_after}
    for station_name in all_station_names:
        junction_numbers_by_name[station_name] = len(adjacent_stations_by_name[station_name])
    for route_pattern in route_patterns:
        stations = route_pattern.stations
        first, last = stations[0], stations[-1]
        for station in route_pattern.station_names:
            is_terminus = station == first or station == last
            is_junction = junction_numbers_by_name[station] > 2
            if is_terminus or is_junction:
                key_station_names.add(station)
    return key_station_names


def get_order_determining_station(
    route_patterns: List[RoutePattern], key_stations: List[str]
) -> str:
    for key_station in key_stations:
        for route_pattern in route_patterns:
            if key_station not in route_pattern.station_names:
                break
        else:
            return key_station


def get_node_timetable(
    route_pattern: RoutePattern, nodes_by_station_name: Dict[str, Node]
) -> Timetable:
    return route_pattern.timetable.map(lambda key: nodes_by_station_name.get(key))


def create_scheduler_network(
    route_patterns: List[RoutePattern], trips_per_hour_by_route_pattern: Dict[str, int]
):
    key_stations = get_key_stations(route_patterns)
    order_determining_station = get_order_determining_station(route_patterns, key_stations)
    nodes_by_station_name = {}
    services_by_route_id = {}

    def get_scheduler_graph_node_by_station_name(station_name: str):
        existing_node = nodes_by_station_name.get(station_name)
        if existing_node:
            return existing_node
        new_node = Node(station_name=station_name)
        nodes_by_station_name[station_name] = new_node
        return new_node

    for route_pattern in route_patterns:
        calls_at_nodes = []
        for station_name in route_pattern.station_names:
            if station_name in key_stations:
                station_node = get_scheduler_graph_node_by_station_name(station_name)
                calls_at_nodes.append(station_node)
        service = Service(
            id=route_pattern.id,
            trips_per_hour=trips_per_hour_by_route_pattern[route_pattern.id],
            calls_at_nodes=calls_at_nodes,
            timetable=get_node_timetable(route_pattern, nodes_by_station_name),
        )
        services_by_route_id[route_pattern.id] = service

    return SchedulerNetwork(
        nodes=nodes_by_station_name,
        order_determining_node=nodes_by_station_name[order_determining_station],
        services=services_by_route_id,
    )
