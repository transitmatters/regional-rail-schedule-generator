import csv
import os

from .config import PATH_TO_GTFS_DATA


def loader_by_file_name(file_name):
    file_path = os.path.join(PATH_TO_GTFS_DATA, file_name + ".txt")

    def load():
        res = []
        with open(file_path, "r") as file:
            dict_reader = csv.DictReader(file)
            for row in dict_reader:
                res.append(row)
        return res

    return load


load_calendar = loader_by_file_name("calendar")
load_calendar_attributes = loader_by_file_name("calendar_attributes")
load_stop_times = loader_by_file_name("stop_times")
load_relevant_stop_times = loader_by_file_name("relevant_stop_times")
load_stops = loader_by_file_name("stops")
load_transfers = loader_by_file_name("transfers")
load_trips = loader_by_file_name("trips")
load_routes = loader_by_file_name("routes")
load_route_patterns = loader_by_file_name("route_patterns")
load_shapes = loader_by_file_name("shapes")
