from typing import List

from synthesize.definitions import RoutePattern
from synthesize.util import get_triples


def get_key_stations(route_patterns: List[RoutePattern]):
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
