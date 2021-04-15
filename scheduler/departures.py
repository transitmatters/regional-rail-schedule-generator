from typing import List, Dict
from datetime import timedelta

from network.models import DIRECTIONS

from synthesize.definitions import Route, RoutePattern, Service, Frequencies, TimeRange
from synthesize.util import listify, get_pairs

from scheduler.network import create_scheduler_network, SchedulerNetwork
from scheduler.scheduling_problem import SchedulingProblem
from scheduler.ordering import get_orderings
from scheduler.optimize import solve_departure_offsets_for_orderings


@listify
def _get_route_patterns(subgraph: List[Route]) -> List[RoutePattern]:
    for route in subgraph:
        for pattern in route.route_patterns:
            yield pattern


def _query_frequencies_dict(frequencies: Frequencies, time: timedelta):
    for (key, value) in frequencies.items():
        (start, end) = key
        if time >= start and time < end:
            return value


def _get_disjoint_time_ranges(time_ranges: List[TimeRange]):
    time_points = set()
    disjoint_ranges = []
    for (start, end) in time_ranges:
        time_points.add(start)
        time_points.add(end)
    for (start, end) in get_pairs(list(sorted(time_points))):
        disjoint_ranges.append((start, end))
    return disjoint_ranges


def _get_constant_frequency_time_ranges(
    route_patterns: List[RoutePattern],
    service: Service,
) -> Dict[TimeRange, Dict[str, int]]:
    schedules = [
        route_pattern.schedule.get(service) for route_pattern in route_patterns
    ]
    time_ranges = [rng for schedule in schedules for rng in schedule.keys()]
    constant_frequency_time_ranges = {}
    disjoint_ranges = _get_disjoint_time_ranges(time_ranges)
    for disjoint_range in disjoint_ranges:
        start_time = disjoint_range[0]
        route_pattern_id_to_tph = {}
        for route_pattern in route_patterns:
            frequencies = route_pattern.schedule.get(service)
            if frequencies is None:
                continue
            frequency_headway = _query_frequencies_dict(frequencies, start_time)
            if frequency_headway:
                trains_per_hour = round(60 / frequency_headway)
                route_pattern_id_to_tph[route_pattern.id] = trains_per_hour
        constant_frequency_time_ranges[disjoint_range] = route_pattern_id_to_tph
    return constant_frequency_time_ranges


@listify
def _get_dispatch_times(tph: int, dispatch_offset: int, rng: TimeRange) -> List[int]:
    headway = 60 / tph
    start, end = rng
    now = start + timedelta(seconds=dispatch_offset)
    while now < end:
        yield now
        now += timedelta(minutes=headway)


def _get_departure_offsets(
    network: SchedulerNetwork, route_pattern_id_to_tph: Dict[str, int]
) -> Dict[str, int]:
    problem = SchedulingProblem(
        trips_per_period=route_pattern_id_to_tph, network=network
    )
    orderings = get_orderings(problem)
    return solve_departure_offsets_for_orderings(problem, orderings)


def get_departures_for_subgraph(subgraph: List[Route], service: Service):
    route_patterns = _get_route_patterns(subgraph)
    constant_frequency_ranges = _get_constant_frequency_time_ranges(
        route_patterns, service
    )
    # previous_arrivals = None
    scheduler_network = create_scheduler_network(route_patterns)
    reverse_scheduler_network = scheduler_network.reverse()
    for (time_range, route_pattern_id_to_tph) in constant_frequency_ranges.items():
        for direction in DIRECTIONS:
            network = scheduler_network if direction == 0 else reverse_scheduler_network
            offsets = _get_departure_offsets(network, route_pattern_id_to_tph)
            for route_pattern in route_patterns:
                route_tph = route_pattern_id_to_tph[route_pattern.id]
                route_offset = offsets[route_pattern.id]
                dispatch_times = _get_dispatch_times(
                    route_tph, route_offset, time_range
                )
                for time in dispatch_times:
                    yield (route_pattern, direction, time)