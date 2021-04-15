from dataclasses import dataclass
from typing import List, Union
from datetime import timedelta

from network.main import get_gtfs_network
from network.models import Network, Service, StopTime, Stop, Trip, Route, RoutePattern
from scheduler.departures import get_departures_for_subgraph

from synthesize.network import create_synthetic_network
import synthesize.definitions as defn
from synthesize.time import Weekdays, Saturday, Sunday

from synthesize.util import listify


@dataclass
class Scenario(object):
    services: List[Service]
    network: Network
    real_network: Network


@listify
def _get_stops_in_direction(
    pattern_defn: defn.RoutePattern,
    direction: int,
    network: Network,
) -> List[Stop]:
    station_names_or_defns = (
        reversed(pattern_defn.stations) if direction == 1 else pattern_defn.stations
    )
    for station_name_or_defn in station_names_or_defns:
        station = _resolve_station(network, station_name_or_defn)
        stop = station.get_child_stop_for_direction(direction)
        yield stop


def _get_routes_for_subgraph(subgraph: List[defn.Route], network: Network):
    for route_defn in subgraph:
        route = Route(id=route_defn.id, long_name=route_defn.name)
        for pattern_defn in route_defn.route_patterns:
            stops = _get_stops_in_direction(pattern_defn, 0, network)
            route_pattern = RoutePattern(
                id=pattern_defn.id, direction=0, stops=stops, route=route
            )
            route.add_route_pattern(route_pattern)
        yield route


@listify
def _get_route_pattern_definitions_from_subgraphs(subgraphs: List[List[defn.Route]]):
    for subgraph in subgraphs:
        for route_defn in subgraph:
            for pattern in route_defn.route_patterns:
                yield pattern


def _resolve_station(network: Network, station_name_or_defn: Union[str, defn.Station]):
    station_name = (
        station_name_or_defn.name
        if isinstance(station_name_or_defn, defn.Station)
        else station_name_or_defn
    )
    return network.get_station_by_name(station_name)


def _add_time_to_trip(
    previous_stop: Stop, current_stop: Stop, route_pattern: defn.RoutePattern
):
    if not previous_stop:
        return timedelta(seconds=0)
    travel_time = route_pattern.timetable.get_travel_time(
        previous_stop.parent_station.name,
        current_stop.parent_station.name,
    )
    return timedelta(seconds=int(travel_time))


def _get_trip(
    trip_index: int,
    route: defn.Route,
    route_pattern: defn.RoutePattern,
    direction: int,
    service: Service,
    departure_time: timedelta,
    network: Network,
) -> List[StopTime]:
    trip = Trip(
        id=f"{route.id}-{trip_index}",
        service=service,
        route_id=route.id,
        route_pattern_id=route_pattern.id,
        direction_id=direction,
        # TODO(ian): add these
        shape_id=None,
        shape=None,
    )
    current_time = departure_time
    previous_stop = None
    for current_stop in _get_stops_in_direction(route_pattern, direction, network):
        current_time += _add_time_to_trip(previous_stop, current_stop, route_pattern)
        previous_stop = current_stop
        stop_time = StopTime(stop=current_stop, trip=trip, time=current_time)
        trip.add_stop_time(stop_time)
    return trip


def _get_trips_for_subgraph(
    subgraph: List[defn.Route],
    services: List[Service],
    network: Network,
) -> List[Trip]:
    trip_index = 0
    for service in services:
        departures = get_departures_for_subgraph(subgraph, service)
        for route_pattern, direction, departure_time in departures:
            route = next((r for r in subgraph if route_pattern in r.route_patterns))
            trip = _get_trip(
                trip_index,
                route,
                route_pattern,
                direction,
                service,
                departure_time,
                network,
            )
            trip_index += 1
            yield trip


def evaluate_scenario(subgraphs: List[List[defn.Route]]) -> Scenario:
    services = [Weekdays, Saturday, Sunday]
    real_network = get_gtfs_network()
    pattern_defns = _get_route_pattern_definitions_from_subgraphs(subgraphs)
    network = create_synthetic_network(real_network, pattern_defns)
    for service in services:
        network.services_by_id[service.id] = service
    for subgraph in subgraphs:
        for route in _get_routes_for_subgraph(subgraph, network):
            network.routes_by_id[route.id] = route
        for trip in _get_trips_for_subgraph(subgraph, services, network):
            network.trips_by_id[trip.id] = trip
    return Scenario(services=services, real_network=real_network, network=network)