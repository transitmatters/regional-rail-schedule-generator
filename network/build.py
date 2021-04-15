from .load import (
    load_relevant_stop_times,
    load_calendar,
    load_calendar_attributes,
    load_shapes,
    load_stops,
    load_transfers,
    load_trips,
    load_routes,
    load_route_patterns,
)
from .models import (
    StopTime,
    Station,
    Stop,
    LocationType,
    Network,
    Transfer,
    Trip,
    Service,
    Route,
    RoutePattern,
)
from .time import time_from_string, DAYS_OF_WEEK


def index_by(items, id_getter):
    res = {}
    if isinstance(id_getter, str):
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
            (lat, lon) for (lat, lon, _) in sorted(res[shape_id], key=lambda entry: entry[2])
        ]
    return res


def link_services(calendar_dicts, calendar_attribute_dicts):
    services = []
    calendar_attributes_by_id = index_by(calendar_attribute_dicts, "service_id")
    for calendar_dict in calendar_dicts:
        service_id = calendar_dict["service_id"]
        attribute_dict = calendar_attributes_by_id[service_id]
        services.append(
            Service(
                id=service_id,
                days=[day for day in DAYS_OF_WEEK if calendar_dict[day] == "1"],
                description=attribute_dict["service_description"],
                schedule_name=attribute_dict["service_schedule_name"],
                schedule_type=attribute_dict["service_schedule_type"],
                schedule_typicality=int(attribute_dict["service_schedule_typicality"]),
            )
        )
    return index_by(services, lambda s: s.id)


def get_stations_from_stops(stop_dicts):
    for stop_dict in stop_dicts:
        if stop_dict["location_type"] == LocationType.STATION:
            yield stop_dict


def get_station_stop_args_from_dict(stop_dict):
    return {
        "id": stop_dict["stop_id"],
        "name": stop_dict["stop_name"],
        "municipality": stop_dict["municipality"],
        "location": (float(stop_dict["stop_lat"]), float(stop_dict["stop_lon"])),
        "wheelchair_boarding": stop_dict["wheelchair_boarding"],
        "on_street": stop_dict["on_street"],
        "at_street": stop_dict["at_street"],
        "vehicle_type": stop_dict["vehicle_type"],
        "zone_id": stop_dict["zone_id"],
        "level_id": stop_dict["level_id"],
        "location_type": stop_dict["location_type"],
    }


def link_station(station_dict):
    return Station(**get_station_stop_args_from_dict(station_dict))


def link_trips(trip_dicts, services_by_id, shapes_by_id):
    res = {}
    for trip_dict in trip_dicts:
        trip_id = trip_dict["trip_id"]
        matching_service = services_by_id.get(trip_dict["service_id"])
        # Throw out special services with no regularly scheduled service days
        if matching_service and len(matching_service.days) > 0:
            trip = Trip(
                id=trip_dict["trip_id"],
                service=matching_service,
                route_id=trip_dict["route_id"],
                route_pattern_id=trip_dict["route_pattern_id"],
                direction_id=int(trip_dict["direction_id"]),
                shape_id=trip_dict["shape_id"],
                shape=shapes_by_id[trip_dict["shape_id"]],
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
            stop = Stop(parent_station=station, **get_station_stop_args_from_dict(stop_dict))
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
                transfer = Transfer(
                    from_stop=stop,
                    to_stop=to_stop,
                    min_walk_time=int(transfer_dict["min_walk_time"] or 0),
                    min_wheelchair_time=int(transfer_dict["min_wheelchair_time"] or 0),
                    min_transfer_time=int(transfer_dict["min_transfer_time"] or 0),
                    suggested_buffer_time=int(transfer_dict["suggested_buffer_time"] or 0),
                    wheelchair_transfer=transfer_dict["wheelchair_transfer"],
                )
                stop.add_transfer(transfer)


def link_routes(route_dicts, route_pattern_dicts):
    routes = []
    for route_dict in route_dicts:
        route_id = route_dict["route_id"]
        route = Route(id=route_id, long_name=route_dict["route_long_name"])
        matching_route_patterns = [
            route_pattern_dict
            for route_pattern_dict in route_pattern_dicts
            if route_pattern_dict["route_id"] == route_id
        ]
        for route_pattern_dict in matching_route_patterns:
            route.route_patterns.append(
                RoutePattern(
                    id=route_pattern_dict["route_pattern_id"],
                    route=route,
                    direction=int(route_pattern_dict["direction_id"]),
                    # TODO(ian): consider filling this in
                    stops=[],
                )
            )
        routes.append(route)
    return index_by(routes, lambda r: r.id)


def ensure_trips_are_sorted(trips_by_id):
    for trip in trips_by_id.values():
        trip.stop_times = list(sorted(trip.stop_times, key=lambda st: st.time))


def build_network_from_gtfs():
    # Do the loading...
    calendar_dicts = load_calendar()
    calendar_attribute_dicts = load_calendar_attributes()
    stop_dicts = load_stops()
    stop_time_dicts = load_relevant_stop_times()
    transfer_dicts = load_transfers()
    trip_dicts = load_trips()
    route_dicts = load_routes()
    route_pattern_dicts = load_route_patterns()
    shapes = load_shapes()
    # Now do the linking...
    station_dicts = get_stations_from_stops(stop_dicts)
    services_by_id = link_services(calendar_dicts, calendar_attribute_dicts)
    routes_by_id = link_routes(route_dicts, route_pattern_dicts)
    shapes_by_id = get_shapes_by_id(shapes)
    trips_by_id = link_trips(trip_dicts, services_by_id, shapes_by_id)
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
        routes_by_id=routes_by_id,
        services_by_id=services_by_id,
    )
