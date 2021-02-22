from typing import List, Dict
from datetime import timedelta

from network.models import DIRECTIONS

from synthesize.definitions import Route, RoutePattern, Service, Frequencies, TimeRange
from synthesize.util import listify, get_pairs, get_triples
from scheduler.takt import get_takt_offsets_for_tph


@listify
def _get_route_patterns(subgraph: List[Route]) -> List[RoutePattern]:
    for route in subgraph:
        for pattern in route.patterns:
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
            if frequency_headway:
                trains_per_hour = round(60 / frequency_headway)
                route_pattern_id_to_tph[route_pattern.id] = trains_per_hour
        constant_frequency_time_ranges[disjoint_range] = route_pattern_id_to_tph
    return constant_frequency_time_ranges


def _get_key_stations(route_patterns: List[RoutePattern]):
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


def _get_takt_determining_station(route_patterns: List[RoutePattern]) -> str:
    key_stations = _get_key_stations(route_patterns)
    for key_station in key_stations:
        for route_pattern in route_patterns:
            if key_station not in route_pattern.station_names:
                break
        else:
            return key_station


def _get_origin_station(route_pattern: RoutePattern, direction: int) -> str:
    origin_station_index = -1 if direction == DIRECTIONS[1] else 0
    return route_pattern.station_names[origin_station_index]


def _get_t0_for_takt_determining_station_by_direction(
    route_patterns: List[RoutePattern], takt_determining_station: str
) -> List[int]:
    res = {}
    for direction in DIRECTIONS:
        min_t0 = float("inf")
        for route_pattern in route_patterns:
            origin_station = _get_origin_station(route_pattern, direction)
            t0 = route_pattern.timetable.get_travel_time(origin_station, takt_determining_station)
            min_t0 = min(min_t0, t0)
        res[direction] = min_t0
    return res


def _get_dispatch_offsets(
    route_patterns: List[RoutePattern],
    takt_offsets: Dict[str, int],
    takt_determining_station: str,
    t0s_by_direction: List[int],
    direction: int,
) -> Dict[str, int]:
    res = {}
    t0 = t0s_by_direction[direction]
    for route_pattern in route_patterns:
        takt_offset = takt_offsets[route_pattern.id]
        origin_station = _get_origin_station(route_pattern, direction)
        time_to_tds = route_pattern.timetable.get_travel_time(
            origin_station, takt_determining_station
        )
        total_offset = time_to_tds - t0 + takt_offset
        res[route_pattern.id] = total_offset
    return res


@listify
def _get_dispatch_times(tph: int, dispatch_offset: int, rng: TimeRange) -> List[int]:
    headway = 60 / tph
    start, end = rng
    now = start + timedelta(seconds=dispatch_offset)
    while now < end:
        yield now
        now += timedelta(minutes=headway)


def schedule_subgraph(subgraph: List[Route], service: Service):
    route_patterns = _get_route_patterns(subgraph)
    constant_frequency_ranges = _get_constant_frequency_time_ranges(route_patterns, service)
    takt_determining_station = _get_takt_determining_station(route_patterns)
    t0_by_direction = _get_t0_for_takt_determining_station_by_direction(
        route_patterns, takt_determining_station
    )
    previous_arrivals = None
    for (rng, route_pattern_id_to_tph) in constant_frequency_ranges.items():
        takt_offsets = get_takt_offsets_for_tph(route_pattern_id_to_tph, previous_arrivals)
        for direction in DIRECTIONS:
            dispatch_offsets = _get_dispatch_offsets(
                route_patterns, takt_offsets, takt_determining_station, t0_by_direction, direction
            )
            for route_pattern in route_patterns:
                tph = route_pattern_id_to_tph[route_pattern.id]
                dispatch_times = _get_dispatch_times(tph, dispatch_offsets[route_pattern.id], rng)
                for time in dispatch_times:
                    yield (route_pattern, direction, time)
