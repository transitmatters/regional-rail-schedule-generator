from typing import Union, List
import csv
import shutil
import os

from network.time import DAYS_OF_WEEK, stringify_timedelta
from network.models import (
    LocationType,
    Stop,
    Station,
    StopTime,
    Service,
    Route,
    Transfer,
    Trip,
    VehicleType,
)
from synthesize.evaluate import Scenario


class GtfsWriter(object):
    def __init__(self, directory_path_from_data):
        self.directory_path = os.path.abspath(
            os.path.join(__file__, "..", "..", "data", directory_path_from_data)
        )
        print(f"Writing to {self.directory_path}")
        self.stop_rows = []
        self.stop_time_rows = []
        self.transfer_rows = []
        self.trip_rows = []
        self.route_rows = []
        self.calendar_rows = []

    def add_route(self, route: Route):
        self.route_rows.append(
            {
                "route_id": route.id,
                "agency_id": "1",
                "route_short_name": "",
                "route_long_name": route.long_name,
                "route_desc": "",
                "route_type": "",
                "route_url": "",
                "route_color": "",
                "route_text_color": "",
                "route_sort_order": "",
                "route_fare_class": "",
                "line_id": "",
                "route": "",
            }
        )

    def add_stop(self, stop: Union[Stop, Station], override_parent_station_id: str = None):
        is_stop = isinstance(stop, Stop)
        location_type = LocationType.STOP if is_stop else LocationType.STATION
        inferred_parent_station_id = stop.parent_station.id if is_stop else ""
        parent_station_id = override_parent_station_id or inferred_parent_station_id
        self.stop_rows.append(
            {
                "stop_id": stop.id,
                "stop_code": stop.id,
                "stop_name": stop.name,
                "stop_desc": "",
                "platform_code": "",
                "platform_name": "",
                "stop_lat": str(stop.location[0]),
                "stop_lon": str(stop.location[1]),
                "zone_id": stop.zone_id,
                "stop_address": "",
                "stop_url": "",
                "level_id": stop.level_id,
                "location_type": location_type,
                "parent_station": parent_station_id,
                "wheelchair_boarding": stop.wheelchair_boarding,
                "municipality": stop.municipality,
                "on_street": stop.on_street,
                "at_street": stop.at_street,
                "vehicle_type": stop.vehicle_type,
            }
        )

    def add_stop_time(self, stop_time: StopTime):
        time = stringify_timedelta(stop_time.time)
        self.stop_time_rows.append(
            {
                "trip_id": stop_time.trip.id,
                "arrival_time": time,
                "departure_time": time,
                "stop_id": stop_time.stop.id,
                "stop_sequence": "",
                "stop_headsign": "",
                "pickup_type": "",
                "drop_off_type": "",
                "timepoint": "",
                "checkpoint_id": "",
            }
        )

    def add_trip(self, trip: Trip):
        self.trip_rows.append(
            {
                "route_id": trip.route_id,
                "service_id": trip.service.id,
                "trip_id": trip.id,
                "trip_headsign": "",
                "trip_short_name": "",
                "direction_id": str(trip.direction_id),
                "block_id": "",
                "shape_id": trip.shape_id,
                "wheelchair_accessible": "",
                "trip_route_type": "",
                "route_pattern_id": trip.route_pattern_id,
                "bikes_allowed": 0,
            }
        )

    def add_transfer(self, transfer: Transfer):
        self.transfer_rows.append(
            {
                "from_stop_id": transfer.from_stop.id,
                "to_stop_id": transfer.to_stop.id,
                "transfer_type": "0",
                "min_transfer_time": transfer.min_transfer_time,
                "min_walk_time": transfer.min_walk_time,
                "min_wheelchair_time": transfer.min_wheelchair_time,
                "suggested_buffer_time": transfer.suggested_buffer_time,
                "wheelchair_transfer": transfer.wheelchair_transfer,
            }
        )

    def add_service(self, service: Service):
        days_dict = {}
        for day in DAYS_OF_WEEK:
            days_dict[day] = "1" if day in service.days else "0"
        self.calendar_rows.append(
            {"service_id": service.id, **days_dict, "start_date": "", "end_date": ""}
        )

    def write_rows_to_csv(self, file_name, rows):
        full_file_path = os.path.join(self.directory_path, file_name + ".txt")
        with open(full_file_path, "w") as file:
            dict_writer = csv.DictWriter(file, fieldnames=rows[0].keys())
            dict_writer.writeheader()
            for row in rows:
                dict_writer.writerow(row)

    def write(self):
        if os.path.exists(self.directory_path) and os.path.isdir(self.directory_path):
            shutil.rmtree(self.directory_path)
        os.mkdir(self.directory_path)
        self.write_rows_to_csv("calendar", self.calendar_rows)
        self.write_rows_to_csv("stops", self.stop_rows)
        self.write_rows_to_csv("stop_times", self.stop_time_rows)
        self.write_rows_to_csv("relevant_stop_times", self.stop_time_rows)
        self.write_rows_to_csv("transfers", self.transfer_rows)
        self.write_rows_to_csv("trips", self.trip_rows)
        self.write_rows_to_csv("routes", self.route_rows)


def get_all_station_ids(scenario: Scenario):
    return set(
        list(scenario.network.stations_by_id.keys())
        + list(scenario.real_network.stations_by_id.keys())
    )


# TODO(ian): This should be like, six functions
def add_synth_to_real_transfers(
    real_stops: List[Stop], synth_stops: List[Stop], writer: GtfsWriter
):
    real_transfers_from_cr_to_non_cr = [
        transfer
        for stop in real_stops
        for transfer in stop.transfers
        if transfer.from_stop.vehicle_type == VehicleType.COMMUTER_RAIL
        and transfer.to_stop.vehicle_type != VehicleType.COMMUTER_RAIL
    ]
    all_non_cr_stop_ids_to_transfer_to = set(
        [transfer.to_stop.id for transfer in real_transfers_from_cr_to_non_cr]
    )
    # For every real non commuter rail stop...
    for non_cr_stop_id in all_non_cr_stop_ids_to_transfer_to:
        # Find a real transfer to this stop
        real_transfer = next(
            real_transfer
            for real_transfer in real_transfers_from_cr_to_non_cr
            if real_transfer.to_stop.id == non_cr_stop_id
        )
        # Link every synthetic stop to this real stop using this transfer to
        # guess transfer time values
        for synth_stop in synth_stops:
            transfer_info_dict = {
                "min_transfer_time": real_transfer.min_transfer_time,
                "min_walk_time": real_transfer.min_walk_time,
                "min_wheelchair_time": real_transfer.min_wheelchair_time,
                "suggested_buffer_time": real_transfer.suggested_buffer_time,
                "wheelchair_transfer": real_transfer.wheelchair_transfer,
            }
            # Make the sorely mistaken assumption that transfers are symmetric
            cr_to_non_cr = Transfer(
                from_stop=synth_stop, to_stop=real_transfer.to_stop, **transfer_info_dict
            )
            non_cr_to_cr = Transfer(
                from_stop=real_transfer.to_stop, to_stop=synth_stop, **transfer_info_dict
            )
            writer.add_transfer(cr_to_non_cr)
            writer.add_transfer(non_cr_to_cr)


def add_real_transfers_for_station(station: Station, writer: GtfsWriter):
    for stop in station.child_stops:
        writer.add_stop(stop)
        for transfer in stop.transfers:
            writer.add_transfer(transfer)


def add_stops(scenario: Scenario, writer: GtfsWriter, station_id: str):
    real_station = scenario.real_network.stations_by_id.get(station_id)
    synth_station = scenario.network.stations_by_id.get(station_id)
    if real_station and synth_station:
        writer.add_stop(synth_station)
        valid_real_stops = [
            stop
            for stop in real_station.child_stops
            if stop.vehicle_type != VehicleType.COMMUTER_RAIL
        ]
        for stop in synth_station.child_stops + valid_real_stops:
            writer.add_stop(stop, synth_station.id)
        for stop in synth_station.child_stops:
            for transfer in stop.transfers:
                writer.add_transfer(transfer)
        for stop in valid_real_stops:
            for transfer in stop.transfers:
                if transfer.to_stop in valid_real_stops:
                    writer.add_transfer(transfer)
        add_synth_to_real_transfers(real_station.child_stops, synth_station.child_stops, writer)
    else:
        existing_station = real_station or synth_station
        writer.add_stop(existing_station)
        for stop in existing_station.child_stops:
            writer.add_stop(stop)
            for transfer in stop.transfers:
                writer.add_transfer(transfer)


def add_trip(trip: Trip, writer: GtfsWriter):
    writer.add_trip(trip)
    for stop_time in trip.stop_times:
        writer.add_stop_time(stop_time)


def write_scenario_gtfs(scenario: Scenario, directory_path):
    writer = GtfsWriter(directory_path)
    all_shadowed_route_ids = scenario.network.routes_by_id.keys()
    all_station_ids = get_all_station_ids(scenario)
    for station_id in all_station_ids:
        add_stops(scenario, writer, station_id)
    for route_id, route in scenario.real_network.routes_by_id.items():
        if route_id not in all_shadowed_route_ids:
            writer.add_route(route)
    for route in scenario.network.routes_by_id.values():
        writer.add_route(route)
    for trip in scenario.real_network.trips_by_id.values():
        if trip.route_id not in all_shadowed_route_ids:
            add_trip(trip, writer)
    for trip in scenario.network.trips_by_id.values():
        add_trip(trip, writer)
    for service in list(scenario.real_network.services_by_id.values()) + list(
        scenario.network.services_by_id.values()
    ):
        writer.add_service(service)
    writer.write()
