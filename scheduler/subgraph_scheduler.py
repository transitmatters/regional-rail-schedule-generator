from typing import List, Dict
from datetime import timedelta

from synthesize.definitions import Route, RoutePattern, Service, Frequencies, TimeRange
from synthesize.util import listify, get_pairs

from scheduler.network import create_scheduler_network
from scheduler.optimize import solve_departure_offsets


@listify
def _get_route_patterns(subgraph: List[Route]) -> List[RoutePattern]:
    for route in subgraph:
        for pattern in route.patterns:
            yield pattern


def _query_frequencies_dict(frequencies: Frequencies, time: timedelta):
    for (key, value) in frequencies.items():
        (start, end) = key
        if time >= start:
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
    route_patterns: List[RoutePattern], service: Service
) -> Dict[TimeRange, Dict[str, int]]:
    schedules = [route_pattern.schedule.get(service) for route_pattern in route_patterns]
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
            trains_per_hour = round(60 / frequency_headway)
            route_pattern_id_to_tph[route_pattern.id] = trains_per_hour
        constant_frequency_time_ranges[disjoint_range] = route_pattern_id_to_tph
    return constant_frequency_time_ranges


def schedule_subgraph(subgraph: List[Route], service: Service) -> Dict[TimeRange, Dict[str, float]]:
    route_patterns = _get_route_patterns(subgraph)
    constant_frequency_ranges = _get_constant_frequency_time_ranges(route_patterns, service)
    offsets_by_time_range = {}
    for (rng, route_pattern_id_to_tph) in constant_frequency_ranges.items():
        route_patterns_in_range = [
            route_pattern
            for route_pattern in route_patterns
            if route_pattern.id in route_pattern_id_to_tph.keys()
        ]
        scheduler_network = create_scheduler_network(
            route_patterns_in_range, route_pattern_id_to_tph
        )
        offsets_by_time_range[rng] = solve_departure_offsets(scheduler_network)
    return offsets_by_time_range
