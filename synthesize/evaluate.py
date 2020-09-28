from dataclasses import dataclass
from typing import List

from network.main import get_gtfs_network
from network.models import Network, Station, Trip, Route, Service
from synthesize.distance import estimate_travel_time_between_stations_seconds
from synthesize.network import create_synthetic_network
from synthesize.definitions import (
    EvalContext,
    Route as RouteDefn,
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


def create_travel_time_estimator(real_network: Network):
    travel_times = {}

    def estimator(from_station: Station, to_station: Station, trainset: Trainset):
        real_from_station = real_network.get_station_by_id(
            from_station.parent_station.id
        )
        real_to_station = real_network.get_station_by_id(to_station.parent_station.id)
        identifier = (real_from_station.id, real_to_station.id)
        if travel_times.get(identifier):
            return travel_times.get(identifier)
        travel_time = estimate_travel_time_between_stations_seconds(
            network=real_network,
            first=real_from_station,
            second=real_to_station,
            trainset=trainset,
        )
        travel_times[identifier] = travel_time
        return travel_time

    return estimator


def evaluate_scenario(route_defns: List[RouteDefn], trainset: Trainset) -> Scenario:
    real_network = get_gtfs_network()
    # TODO(ian): this should not return a whole network
    network = create_synthetic_network(real_network, route_defns, [])
    ctx = EvalContext(
        network=network,
        trainset=trainset,
        estimate_travel_time=create_travel_time_estimator(real_network),
    )
    for service in (Weekdays, Saturday, Sunday):
        network.services_by_id[service.id] = service
    for route_defn in route_defns:
        route, trips_for_route = schedule_route(route_defn, ctx)
        for trip in trips_for_route:
            network.trips_by_id[trip.id] = trip
        network.routes_by_id[route.id] = route
    return Scenario(
        network=network,
        real_network=real_network,
        services=[Weekdays, Saturday, Sunday],
    )
