from typing import List, Union

from network.models import (
    Station,
    Network,
    Stop,
    Transfer,
    LocationType,
    VehicleType,
    DIRECTIONS,
)

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


def create_two_track_station(real_station: Station):
    station_values = {
        "wheelchair_boarding": real_station.wheelchair_boarding,
        "municipality": real_station.municipality,
        "on_street": real_station.on_street,
        "at_street": real_station.at_street,
        "zone_id": real_station.zone_id,
        "level_id": real_station.level_id,
        "location": real_station.location,
    }
    station = Station(
        name=real_station.name,
        id=real_station.id,
        **{**station_values, "location_type": LocationType.STATION, "vehicle_type": ""},
    )
    for direction in DIRECTIONS:
        child_stop = Stop(
            parent_station=station,
            id=f"{real_station.id}-{direction}",
            name=f"platform {direction}",
            **{
                **station_values,
                "location_type": LocationType.STOP,
                "vehicle_type": VehicleType.COMMUTER_RAIL,
            },
        )
        station.add_child_stop(child_stop)
        station.tag_child_stop_with_direction(child_stop, direction)
    # Don't @ me
    # TODO(ian): take a better guess at these
    transfer_time_values = {
        "min_transfer_time": 180,
        "min_walk_time": 120,
        "min_wheelchair_time": 180,
        "suggested_buffer_time": 60,
        "wheelchair_transfer": "1",
    }
    for child_stop in station.child_stops:
        for other_child_stop in station.child_stops:
            if child_stop != other_child_stop:
                child_stop.add_transfer(
                    Transfer(
                        from_stop=child_stop, to_stop=other_child_stop, **transfer_time_values,
                    )
                )
    return station


def get_all_station_names(station_names: Union[List[str], defn.Branching]) -> List[str]:
    if isinstance(station_names, defn.Branching):
        return set(
            [
                *station_names.shared_station_names,
                *[
                    name
                    for branch in station_names.branch_station_names
                    for name in get_all_station_names(branch)
                ],
            ]
        )
    return set(station_names)


def create_synthetic_network(
    real_network: Network, routes: List[defn.Route], stations: List[Station],
) -> Network:
    network = Network({}, {}, {}, {}, {})
    for synth_station in stations:
        network.add_station(create_two_track_station(synth_station))
    for route in routes:
        for station_name in get_all_station_names(route.stations):
            real_station = real_network.get_station_by_name(station_name)
            if real_station and not network.get_station_by_id(real_station.id):
                station = create_two_track_station(real_station)
                network.add_station(station)
    return network
