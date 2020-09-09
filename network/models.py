from dataclasses import dataclass, field
from typing import List, Tuple, Dict, Optional
import functools
import datetime

DIRECTIONS = (0, 1)


class LocationType:
    STOP = "0"
    STATION = "1"


@dataclass
class Trip(object):
    id: str
    service_id: str
    route_id: str
    shape_id: str
    shape: List[Tuple[float, float]]
    direction_id: int
    service_days: List[str]

    def __post_init__(self):
        self.stop_times = []

    def add_stop_time(self, stop_time):
        self.stop_times.append(stop_time)


@dataclass
class Direction(object):
    id: str
    route: "Route"
    direction: str
    destination: str


@dataclass
class Station(object):
    id: str
    name: str
    location: Tuple[float, float]

    def __str__(self):
        return f"Station({self.id})"

    def __post_init__(self):
        self.child_stops = []
        self.child_stops_by_direction = {}

    def add_child_stop(self, stop):
        self.child_stops.append(stop)

    def tag_child_stop_with_direction(self, stop, direction):
        assert stop in self.child_stops
        self.child_stops_by_direction[direction] = stop

    def get_child_stop_for_direction(self, direction):
        return self.child_stops_by_direction[direction]


@dataclass
class Stop(object):
    parent_station: Station
    id: str
    name: str

    def __str__(self):
        return f"Stop({self.parent_station.id}.{self.id})"

    def __post_init__(self):
        self.stop_times = []
        self.transfers = []

    def set_stop_times(self, stop_times):
        self.stop_times = stop_times

    def add_transfer(self, transfer):
        self.transfers.append(transfer)


@functools.total_ordering
@dataclass
class StopTime(object):
    stop: Stop
    trip: Trip
    time: datetime.timedelta

    def __eq__(self, other):
        return self.time == other.time

    def __ne__(self, other):
        return self.time != other.time

    def __lt__(self, other):
        return self.time < other.time


@dataclass
class Transfer(object):
    from_stop: Stop
    to_stop: Stop
    min_walk_time: int


@dataclass
class Network(object):
    stations_by_id: Dict[str, Station]
    trips_by_id: Dict[str, Trip]
    shapes_by_id: Dict[str, List[Tuple[float, float]]]

    def add_station(self, station: Station):
        existing_station_by_id = self.stations_by_id.get(station.id)
        if existing_station_by_id:
            raise NameError(f"Station with id ${station.id} already exists in network")
        self.stations_by_id[station.id] = station
        return station

    def get_station_by_id(self, station_id: str) -> Optional[Station]:
        return self.stations_by_id.get(station_id)

    def get_station_by_name(self, station_name: str) -> Optional[Station]:
        for station in self.stations_by_id.values():
            if station.name == station_name:
                return station
        return None


@dataclass
class RoutePattern(object):
    id: str
    route: "Route"
    direction: int
    stops: List[Stop]


@dataclass
class Route(object):
    id: str
    long_name: str
    representative_trip: Trip = None
    route_patterns: List[RoutePattern] = field(default_factory=list)

    def add_route_pattern(self, pattern: RoutePattern):
        self.route_patterns.append(pattern)
        pattern.route = self


@dataclass
class Service(object):
    id: str
    days: List[str]
