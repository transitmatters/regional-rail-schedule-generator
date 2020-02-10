class LocationType:
    STOP = "0"
    STATION = "1"


class Service(object):
    def __init__(self):
        pass


class Station(object):
    def __init__(self):
        self.child_stops = []

    def add_child_stop(self, stop):
        self.child_stops.append(stop)


class Stop(object):
    def __init__(self):
        self.stop_times = []

    def set_stop_times(self, stop_times):
        self.stop_times = stop_times


class StopTime(object):
    def __init__(self):
        pass


class Transfer(object):
    def __init__(self):
        pass


def link_station(station_dict):
    return None


def link_stop_times(stop, stop_time_dicts, trip_dicts_by_id):
    stop_times = []
    for stop_time_dict in stop_time_dicts:
        if stop_time_dict["stop_id"] == stop.id:
            trip = trip_dicts_by_id.get(stop_time_dict["trip_id"])
            if trip:
                stop_time = StopTime(stop=stop, trip=trip, **stop_time_dict)
                stop_times.append(stop_time)
                trip.add_stop_time(stop_time)
    stop.set_stop_times(sorted(stop_times))


def link_child_stops(station, stop_dicts):
    for stop_dict in stop_dicts:
        if (
            stop_dict["parent_station"] == station.id
            and stop_dict["location_type"] == LocationType.STOP
        ):
            stop = Stop(parent_station=station, **stop_dict)
            yield stop
            if len(stop.stop_times > 0):
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
                transfer = Transfer(from_stop=stop, to_stop=to_stop, **transfer_dict)
                stop.add_transfer(transfer)


def build_network_from_gtfs():
    # Do the loading...
    service_dicts = load_services()
    stop_dicts = load_stops()
    stop_time_dicts = load_stop_times()
    transfer_dicts = load_transfers()
    trip_dicts = load_trips(service_dicts)
    station_dicts = get_stations_from_stops(stop_dicts)
    trip_dicts_by_id = get_trip_dicts_by_id(trip_dicts)
    # Now do the linking...
    stations = [link_station(d) for d in station_dicts]
    all_stops = []
    for station in stations:
        for child_stop in link_child_stops(station, stop_dicts):
            all_stops.append(child_stop)
            link_stop_times(child_stop, stop_time_dicts, trip_dicts_by_id)
    for station in stations:
        for stop in station.stops:
            link_transfers(stop, all_stops, transfer_dicts)
