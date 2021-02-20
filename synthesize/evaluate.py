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
from scheduler.subgraph_scheduler import schedule_subgraph

from synthesize.network import create_synthetic_network
from synthesize.definitions import (
    Route as RouteDefn,
    Station as StationDefn,
)
from synthesize.time import Weekdays, Saturday, Sunday
from synthesize.trainset import Trainset

# from synthesize.naive_scheduler import schedule_route
from synthesize.util import listify


@dataclass
class Scenario(object):
    services: List[Service]
    network: Network
    real_network: Network


@listify
def get_route_patterns_from_subgraphs(subgraphs: List[List[RouteDefn]]):
    for subgraph in subgraphs:
        for route_defn in subgraph:
            for pattern in route_defn.patterns:
                yield pattern


def evaluate_scenario(subgraphs: List[List[RouteDefn]]) -> Scenario:
    real_network = get_gtfs_network()
    route_patterns = get_route_patterns_from_subgraphs(subgraphs)
    network = create_synthetic_network(real_network, route_patterns)
    for service in (Weekdays, Saturday, Sunday):
        network.services_by_id[service.id] = service
        for subgraph in subgraphs:
            offsets = schedule_subgraph(subgraph, service)
            print(offsets)
        # route, trips_for_route = schedule_route(route_defn, ctx)
        # for trip in trips_for_route:
        #     network.trips_by_id[trip.id] = trip
        # network.routes_by_id[route.id] = route
    # return Scenario(
    #     network=network,
    #     real_network=real_network,
    #     services=[Weekdays, Saturday, Sunday],
    # )
