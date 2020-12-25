from dataclasses import dataclass
from typing import List

from network.main import get_gtfs_network
from network.models import (
    LocationType,
    Network,
    Service,
    Station,
    Stop,
    VehicleType,
)
from synthesize.distance import estimate_travel_time_between_stations_seconds
from synthesize.network import create_synthetic_network
from synthesize.definitions import (
    EvalContext,
    Route as RouteDefn,
    Station as StationDefn,
    Weekdays,
    Saturday,
    Sunday,
)
from synthesize.trainset import Trainset
from synthesize.naive_scheduler import schedule_route


@dataclass
class Scenario(object):
    services: List[Service]
    network: Network
    real_network: Network


def get_provided_travel_time(
    route_defns: List[RouteDefn], from_station: Station, to_station: Station
):
    for route_defn in route_defns:
        if route_defn.travel_times:
            from_time = route_defn.travel_times.get(from_station.name)
            to_time = route_defn.travel_times.get(to_station.name)
            if from_time is not None and to_time is not None:
                return abs(from_time - to_time).seconds
    return None


def get_estimated_travel_time(
    real_network: Network, from_station: Station, to_station: Station, trainset: Trainset,
):
    real_from_station = real_network.get_station_by_id(from_station.id)
    real_to_station = real_network.get_station_by_id(to_station.id)
    print(f"Warning: estimating travel time for {real_from_station} -> {real_to_station}")
    return estimate_travel_time_between_stations_seconds(
        network=real_network, first=real_from_station, second=real_to_station, trainset=trainset,
    )


def create_travel_time_source(real_network: Network, route_defns: List[RouteDefn]):
    travel_times = {}

    def estimator(from_stop: Stop, to_stop: Stop, trainset: Trainset):
        from_station = from_stop.parent_station
        to_station = to_stop.parent_station
        identifier = tuple(sorted((from_station.id, to_station.id)))
        computed_travel_time = travel_times.get(identifier)
        if computed_travel_time:
            return computed_travel_time
        travel_time = get_provided_travel_time(
            route_defns, from_station, to_station
        ) or get_estimated_travel_time(real_network, from_station, to_station, trainset)
        travel_times[identifier] = travel_time
        return travel_time

    return estimator


def create_station_from_station_defn(station_defn: StationDefn) -> Station:
    return Station(
        id=station_defn.id,
        name=station_defn.name,
        municipality=station_defn.municipality,
        location=station_defn.location,
        vehicle_type=VehicleType.COMMUTER_RAIL,
        location_type=LocationType.STATION,
        wheelchair_boarding="1",
        zone_id="",  # TODO: abolish fare zones
        on_street="",
        at_street="",
        level_id="",
    )


def evaluate_scenario(
    route_defns: List[RouteDefn], trainset: Trainset, station_defns: List[StationDefn]
) -> Scenario:
    real_network = get_gtfs_network()
    stations = [create_station_from_station_defn(defn) for defn in station_defns]
    network = create_synthetic_network(real_network, route_defns, stations)
    ctx = EvalContext(
        network=network,
        trainset=trainset,
        get_travel_time=create_travel_time_source(real_network, route_defns),
    )
    for service in (Weekdays, Saturday, Sunday):
        network.services_by_id[service.id] = service
    for route_defn in route_defns:
        route, trips_for_route = schedule_route(route_defn, ctx)
        for trip in trips_for_route:
            network.trips_by_id[trip.id] = trip
        network.routes_by_id[route.id] = route
    return Scenario(
        network=network, real_network=real_network, services=[Weekdays, Saturday, Sunday],
    )
