from typing import List, Union

from network.models import Station, Network, Stop, DIRECTIONS

import synthesize.definitions as defn


def create_four_track_station(name, id, **kwargs):
    station = Station(name=name, id=id, **kwargs)
    for child_stop in (
        Stop(station, "northbound-1", "Northbound platform 1"),
        Stop(station, "northbound-2", "Northbound platform 2"),
        Stop(station, "southbound-1", "Southbound platform 1"),
        Stop(station, "southbound-2", "Southbound platform 2"),
    ):
        station.add_child_stop(child_stop)
    return station


def create_two_track_station(name, id, **kwargs):
    station = Station(name=name, id=id, **kwargs)
    for direction in DIRECTIONS:
        child_stop = Stop(station, f"{id}-direction", f"platform {direction}")
        station.add_child_stop(child_stop)
        station.tag_child_stop_with_direction(child_stop, direction)
    return station


def get_real_gtfs_station(real_gtfs_network: Network, station_name: str) -> Station:
    real_gtfs_station = real_gtfs_network.get_station_by_name(station_name)
    if not real_gtfs_station:
        raise Exception(f"No real GTFS station by name {station_name}")
    return real_gtfs_station


def get_all_station_names(station_names: Union[List[str], defn.Branching]) -> List[str]:
    if isinstance(station_names, defn.Branching):
        return set([
            *station_names.shared_station_names,
            *[
                name
                for branch in station_names.branch_station_names
                for name in get_all_station_names(branch)
            ],
        ])
    return set(station_names)


def create_synthetic_network(
    real_network: Network, routes: List[defn.Route], stations: List[Station],
) -> Network:
    network = Network({}, {}, {})
    for synth_station in stations:
        network.add_station(synth_station)
    for route in routes:
        for station_name in get_all_station_names(route.stations):
            real_station = get_real_gtfs_station(real_network, station_name)
            if not network.get_station_by_id(real_station.id):
                station = create_two_track_station(
                    name=real_station.name,
                    id=real_station.id,
                    location=real_station.location,
                )
                network.add_station(station)
    return network
