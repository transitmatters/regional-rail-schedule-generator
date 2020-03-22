from typing import List

from network.models import Network, Station, Trip
from .trainset import Trainset
from .distance import estimate_travel_time_between_stations_seconds, get_pairs


def estimate_total_route_time(
    route: List[str], network: Network, trainset: Trainset, dwell_time_seconds=45
):
    total_time_seconds = 0
    for first_station_name, second_station_name in get_pairs(route):
        first_station = network.get_station_by_name(first_station_name)
        second_station = network.get_station_by_name(second_station_name)
        total_time_seconds += (
            dwell_time_seconds
            + estimate_travel_time_between_stations_seconds(
                network, first_station, second_station, trainset
            )
        )
    return total_time_seconds
