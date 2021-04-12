from typing import List, Union
from datetime import timedelta

from network.models import (
    DIRECTIONS,
    Network,
    Route,
    RoutePattern,
    Service,
    Stop,
    StopTime,
    Trip,
)
import synthesize.definitions as defn
from synthesize.util import listify, get_pairs


@listify
def get_stops_in_direction(
    station_names: List[str], direction: int, network: Network
) -> List[Stop]:
    d_station_names = reversed(station_names) if direction == 1 else station_names
    for station_name in d_station_names:
        station = network.get_station_by_name(station_name)
        yield station.get_child_stop_for_direction(direction)


# @listify
# def get_route_patterns_for_direction(
#     route: Route, route_defn: defn.Route, network: Network, direction: int
# ):
#     for idx, path in enumerate(get_all_branch_paths(route_defn.stations)):
#         yield RoutePattern(
#             id=f"{route_defn.id}-{direction}-{idx}",
#             route=route,
#             direction=direction,
#             stops=get_stops_in_direction(path, direction, network),
#         )


@listify
def get_route_patterns_by_direction(
    route: defn.Route, route_defn: defn.Route, network: Network
) -> List[List[RoutePattern]]:
    for idx, direction in enumerate(DIRECTIONS):
        # By convention, directions are (0, 1)
        assert direction == idx
        yield get_route_patterns_for_direction(route, route_defn, network, direction)


def add_time_to_trip(previous_stop: Stop, current_stop: Stop, ctx: defn.EvalContext):
    if not previous_stop:
        return timedelta(seconds=0)
    travel_time = ctx.get_travel_time(previous_stop, current_stop, ctx.trainset)
    return timedelta(seconds=int(ctx.trainset.dwell_time_seconds + travel_time))


def schedule_route(route_defn: defn.Route, ctx: defn.EvalContext) -> List[Trip]:
    route = Route(id=route_defn.id, long_name=route_defn.name)
    route_patterns = get_route_patterns_by_direction(route, route_defn, ctx.network)
    trips = []

    for direction in DIRECTIONS:
        for route_pattern in route_patterns[direction]:
            route.add_route_pattern(route_pattern)

    for (service, frequencies) in route_defn.schedule.items():
        dispatch = dispatch_trains(frequencies, route_patterns)
        for idx, (route_pattern, time) in enumerate(dispatch):
            trip = get_trip(
                trip_index=idx,
                route=route_defn,
                route_pattern=route_pattern,
                service=service,
                departure_time=time,
                ctx=ctx,
            )
            trips.append(trip)

    return route, trips
