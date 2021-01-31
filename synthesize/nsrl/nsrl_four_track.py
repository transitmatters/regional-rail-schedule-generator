from typing import List, Tuple

import networkx as nx

import network

from synthesize.nsrl.constraint_scheduler_wip import (
    build_scheduler_graph,
    solve_schedule,
)
from synthesize.nsrl.stations import (
    create_four_track_station,
    create_network_from_routes_and_real_network,
    create_nsrl_route,
)
from synthesize.routes import (
    ALL_ROUTES,
    EASTERN_ROCKPORT,
    FRAMINGHAM_WORCESTER,
    FITCHBURG,
    OC_KINGSTON_PLYMOUTH,
)

real_network = network.get_gtfs_network()

north_station = create_four_track_station(
    name="North Station",
    id="place-north",
    location=real_network.get_station_by_name("North Station").location,
)

south_station = create_four_track_station(
    name="South Station",
    id="place-sstat",
    location=real_network.get_station_by_name("South Station").location,
)

synth_network = create_network_from_routes_and_real_network(
    [north_station, south_station], ALL_ROUTES, real_network
)

test_route_a = create_nsrl_route(
    network=synth_network,
    northside_station_names=EASTERN_ROCKPORT,
    southside_station_names=FRAMINGHAM_WORCESTER,
    nsrl_tunnel_number=1,
)

test_route_b = create_nsrl_route(
    network=synth_network,
    northside_station_names=FITCHBURG,
    southside_station_names=OC_KINGSTON_PLYMOUTH,
    nsrl_tunnel_number=1,
)

routes = {"test_route_a": {"route": test_route_a, "service_frequency_tph": 6}}


def get_ids_for_route(route: List[network.models.Stop]):
    return [s.parent_station.id for s in route]


print(get_ids_for_route(test_route_a))
