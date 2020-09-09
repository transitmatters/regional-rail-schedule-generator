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
    synth_stations: List[Station], routes: List[Tuple[str]], real_network: Network
) -> Network:
    network = Network({}, {}, {})
    for synth_station in synth_stations:
        network.add_station(synth_station)
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


def create_nsrl_route(
    network: Network,
    northside_station_names: List[str],
    southside_station_names: List[str],
    nsrl_tunnel_number: int,
    direction: str = "southbound",
) -> List[Stop]:
    north_station = network.get_station_by_name(northside_station_names[0])
    south_station = network.get_station_by_name(southside_station_names[0])
    assert north_station.name == "North Station"
    assert south_station.name == "South Station"

    def find_child_stop_by_id(station: Station, id: str):
        try:
            return next(stop for stop in station.child_stops if stop.id == id)
        except StopIteration as e:
            raise Exception(
                f"station {station.name} has no child_stop by id {id}. Has {station.child_stops}"
            ) from e

    two_track_stop_name = direction
    four_track_stop_name = f"{direction}-{str(nsrl_tunnel_number)}"

    northside_stops = [
        find_child_stop_by_id(
            network.get_station_by_name(station_name), two_track_stop_name
        )
        for station_name in northside_station_names[1:]
    ]

    tunnel = [
        find_child_stop_by_id(station, four_track_stop_name)
        for station in [north_station, south_station]
    ]

    southside_stops = [
        find_child_stop_by_id(
            network.get_station_by_name(station_name), two_track_stop_name
        )
        for station_name in southside_station_names[1:]
    ]

    return list(reversed(northside_stops)) + tunnel + southside_stops
