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
def get_all_branch_paths(
    station_names: Union[List[str], defn.Branching]
) -> List[List[str]]:
    if isinstance(station_names, defn.Branching):
        for sub_path in station_names.branch_station_names:
            all_paths_in_sub_path = get_all_branch_paths(sub_path)
            for path in all_paths_in_sub_path:
                yield [*list(station_names.shared_station_names), *list(path)]
    else:
        yield list(station_names)


@listify
def get_stops_in_direction(
    station_names: List[str], direction: int, network: Network
) -> List[Stop]:
    d_station_names = reversed(station_names) if direction == 1 else station_names
    for station_name in d_station_names:
        station = network.get_station_by_name(station_name)
        yield station.get_child_stop_for_direction(direction)


@listify
def get_route_patterns_for_direction(
    route: Route, route_defn: defn.Route, network: Network, direction: int
):
    for idx, path in enumerate(get_all_branch_paths(route_defn.stations)):
        yield RoutePattern(
            id=f"{route_defn.id}-{direction}-{idx}",
            route=route,
            direction=direction,
            stops=get_stops_in_direction(path, direction, network),
        )


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
    travel_time = ctx.estimate_travel_time(previous_stop, current_stop, ctx.trainset)
    return timedelta(seconds=int(ctx.trainset.dwell_time_seconds + travel_time))


def get_trip(
    trip_index: str,
    route: defn.Route,
    route_pattern: RoutePattern,
    service: Service,
    departure_time: timedelta,
    ctx: defn.EvalContext,
) -> List[StopTime]:
    trip = Trip(
        id=f"{route.id}-{trip_index}",
        service=service,
        route_id=route.id,
        route_pattern_id=route_pattern.id,
        direction_id=route_pattern.direction,
        # TODO(ian): add these
        shape_id=None,
        shape=None,
    )
    current_time = departure_time
    previous_stop = None
    for current_stop in route_pattern.stops:
        current_time += add_time_to_trip(previous_stop, current_stop, ctx)
        previous_stop = current_stop
        stop_time = StopTime(stop=current_stop, trip=trip, time=current_time)
        trip.add_stop_time(stop_time)
    return trip


def dispatch_trains(
    frequencies: defn.Frequencies, patterns_by_dir: List[List[RoutePattern]]
):
    # There should the same number of patterns for each direction
    assert len(set([len(patterns) for patterns in patterns_by_dir])) == 1
    route_pattern_index = 0
    ordered_ranges = list(frequencies.keys())
    # Route frequences must be normalized (ordered and non-overlapping ranges)
    for (range_a, range_b) in get_pairs(ordered_ranges):
        (start_a, end_a) = range_a
        (start_b, _) = range_b
        assert start_a < end_a
        assert end_a <= start_b
    now = ordered_ranges[0][0]
    current_range_idx = 0
    while True:
        for patterns in patterns_by_dir:
            route_pattern = patterns[route_pattern_index]
            yield route_pattern, now
        route_pattern_index = (route_pattern_index + 1) % len(patterns)
        current_range = ordered_ranges[current_range_idx]
        advance_time_by = frequencies[current_range]
        now += timedelta(minutes=advance_time_by)
        if now > current_range[1]:
            current_range_idx += 1
            if current_range_idx == len(ordered_ranges):
                return


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
