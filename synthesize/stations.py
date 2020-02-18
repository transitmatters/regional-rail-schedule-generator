from typing import List, Tuple

from network.models import Station, Stop, Network


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
    for child_stop in (
        Stop(station, "northbound", "Northbound platform"),
        Stop(station, "southbound", "Southbound platform"),
    ):
        station.add_child_stop(child_stop)
    return station


def get_real_gtfs_station(real_gtfs_network: Network, station_name: str) -> Station:
    real_gtfs_station = real_gtfs_network.get_station_by_name(station_name)
    if not real_gtfs_station:
        raise Exception(f"No real GTFS station by name {station_name}")
    return real_gtfs_station


def create_network_from_routes_and_real_network(
    key_stations: List[Station], routes: List[Tuple[str]], real_network: Network
) -> Network:
    network = Network({}, {})
    for key_station in key_stations:
        network.add_station(key_station)
    for route in routes:
        for station_name in route:
            real_station = get_real_gtfs_station(real_network, station_name)
            if not network.get_station_by_id(real_station.id):
                station = create_two_track_station(
                    name=real_station.name,
                    id=real_station.id,
                    location=real_station.location,
                )
                network.add_station(station)
    return network
