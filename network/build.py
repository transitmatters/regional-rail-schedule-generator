from .load import (
    load_relevant_stop_times,
    load_services,
    load_shapes,
    load_stops,
    load_transfers,
    load_trips,
)
from .models import StopTime, Station, Stop, LocationType, Network, Transfer, Trip
from .time import time_from_string, DAYS_OF_WEEK


def index_by(items, id_getter):
    res = {}
    if type(id_getter) == str:
        id_getter_as_str = id_getter
        id_getter = lambda dict: dict[id_getter_as_str]
    for a_dict in items:
        res[id_getter(a_dict)] = a_dict
    return res


def get_shapes_by_id(shapes):
    res = {}
    for shape in shapes:
        shape_id = shape["shape_id"]
        if not res.get(shape_id):
            res[shape_id] = []
        lat = float(shape["shape_pt_lat"])
        lon = float(shape["shape_pt_lon"])
        seq = int(shape["shape_pt_sequence"])
        res[shape_id].append((lat, lon, seq))
    for shape_id in res:
        res[shape_id] = [
            (lat, lon)
            for (lat, lon, _) in sorted(res[shape_id], key=lambda entry: entry[2])
        ]
    return res


def get_stations_from_stops(stop_dicts):
    for stop_dict in stop_dicts:
        if stop_dict["location_type"] == LocationType.STATION:
            yield stop_dict


def link_station(station_dict):
    return Station(
        id=station_dict["stop_id"],
        name=station_dict["stop_name"],
        location=(float(station_dict["stop_lat"]), float(station_dict["stop_lon"])),
    )


def link_trips(trip_dicts, service_dicts, shapes_by_id):
    res = {}
    services_by_id = index_by(service_dicts, "service_id")
    for trip_dict in trip_dicts:
        trip_id = trip_dict["trip_id"]
        matching_service = services_by_id.get(trip_dict["service_id"])
        if matching_service:
            service_days = [day for day in DAYS_OF_WEEK if matching_service[day] == "1"]
            # Throw out special services with no regularly scheduled service days
            if len(service_days) > 0:
                trip = Trip(
                    id=trip_dict["trip_id"],
                    service_id=trip_dict["service_id"],
                    route_id=trip_dict["route_id"],
                    direction_id=int(trip_dict["direction_id"]),
                    shape_id=trip_dict["shape_id"],
                    shape=shapes_by_id[trip_dict["shape_id"]],
                    service_days=service_days,
                )
                res[trip_id] = trip
    return res


def link_stop_times(stop, stop_time_dicts, trips_by_id):
    stop_times = []
    added = 0
    for stop_time_dict in stop_time_dicts:
        if stop_time_dict["stop_id"] == stop.id:
            trip = trips_by_id.get(stop_time_dict["trip_id"])
            if trip:
                stop_time = StopTime(
                    stop=stop,
                    trip=trip,
                    time=time_from_string(stop_time_dict["departure_time"]),
                )
                added += 1
                stop_times.append(stop_time)
                trip.add_stop_time(stop_time)
    stop.set_stop_times(sorted(stop_times))


def link_child_stops(station, stop_dicts):
    for stop_dict in stop_dicts:
        if (
            stop_dict["parent_station"] == station.id
            and stop_dict["location_type"] == LocationType.STOP
        ):
            stop = Stop(
                parent_station=station,
                id=stop_dict["stop_id"],
                name=stop_dict["stop_name"],
            )
            yield stop
            if len(stop.stop_times) > 0:
                station.add_child_stop(stop)


def link_transfers(stop, all_stops, transfer_dicts):
    for transfer_dict in transfer_dicts:
        if transfer_dict["from_stop_id"] == stop.id:
            to_stop = next(
                (
                    other_stop
                    for other_stop in all_stops
                    if other_stop.id == transfer_dict["to_stop_id"]
                ),
                None,
            )
            if to_stop:
                min_walk_time_raw = transfer_dict["min_walk_time"]
                min_walk_time = (
                    int(min_walk_time_raw) if len(min_walk_time_raw) else None
                )
                transfer = Transfer(
                    from_stop=stop, to_stop=to_stop, min_walk_time=min_walk_time,
                )
                stop.add_transfer(transfer)


def ensure_trips_are_sorted(trips_by_id):
    for trip in trips_by_id.values():
        trip.stop_times = list(sorted(trip.stop_times, key=lambda st: st.time))


def build_network_from_gtfs():
    # Do the loading...
    service_dicts = load_services()
    stop_dicts = load_stops()
    stop_time_dicts = load_relevant_stop_times()
    transfer_dicts = load_transfers()
    trip_dicts = load_trips()
    shapes = load_shapes()
    # Now do the linking...
    station_dicts = get_stations_from_stops(stop_dicts)
    shapes_by_id = get_shapes_by_id(shapes)
    trips_by_id = link_trips(trip_dicts, service_dicts, shapes_by_id)
    stations = [link_station(d) for d in station_dicts]
    all_stops = []
    for station in stations:
        for child_stop in link_child_stops(station, stop_dicts):
            all_stops.append(child_stop)
            link_stop_times(child_stop, stop_time_dicts, trips_by_id)
    for station in stations:
        for stop in station.child_stops:
            link_transfers(stop, all_stops, transfer_dicts)
    ensure_trips_are_sorted(trips_by_id)
    return Network(
        stations_by_id=index_by(stations, lambda st: st.id),
        trips_by_id=trips_by_id,
        shapes_by_id=shapes_by_id,
    )
