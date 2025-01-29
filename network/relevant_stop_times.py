import csv
import os

from .load import load_stop_times, load_trips
from .build import index_by
from .config import PATH_TO_GTFS_DATA

PATH_TO_OUTPUT = os.path.join(PATH_TO_GTFS_DATA, "relevant_stop_times.txt")

RAPID_TRANSIT = (
    "Orange",
    "Red",
    "Blue",
    "Green-B",
    "Green-C",
    "Green-D",
    "Green-E",
)

SILVER_LINE = (
    "741",
    "742",
    "743",
    "751",
    "749",
    "746",
)

RELEVANT_ROUTE_IDS = RAPID_TRANSIT + SILVER_LINE


def is_relevant_route_id(route_id):
    return route_id in RELEVANT_ROUTE_IDS or route_id.startswith("CR-")


def is_relevant_stop_time(stop_time_dict, trip_dicts_by_id):
    trip_dict = trip_dicts_by_id.get(stop_time_dict["trip_id"])
    if trip_dict:
        return is_relevant_route_id(trip_dict["route_id"])
    return False


def generate_relevant_stop_times():
    trip_dicts_by_id = index_by(load_trips(), "trip_id")
    stop_times = load_stop_times()
    relevant_stop_times = [stop_time for stop_time in stop_times if is_relevant_stop_time(stop_time, trip_dicts_by_id)]
    with open(PATH_TO_OUTPUT, "w") as file:
        fieldnames = relevant_stop_times[0].keys()
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for stop_time in relevant_stop_times:
            writer.writerow(stop_time)


if __name__ == "__main__":
    generate_relevant_stop_times()
