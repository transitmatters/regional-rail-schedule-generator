from dataclasses import dataclass, field
from functools import cached_property
from typing import Dict, List, Tuple, Union
from datetime import timedelta

from network.models import Service
from synthesize.time import Timetable
from synthesize.trainset import Trainset
from synthesize.util import listify
from synthesize.amenities import Amenities

TimeRange = Tuple[timedelta, timedelta]
Frequencies = Dict[TimeRange, int]
Schedule = Dict[Service, Frequencies]


@dataclass
class Station(object):
    name: str
    id: str
    location: str
    municipality: str


@dataclass
class RoutePattern(object):
    id: str
    stations: List[Union[str, Station]]
    timetable: Timetable
    schedule: Schedule
    name: str = None
    trainset: Trainset = None
    amenities: Amenities = field(default_factory=Amenities)

    def __post_init__(self):
        self.parent_route = None
        for station in self.stations:
            station_name = station.name if isinstance(station, Station) else station
            assert self.timetable.contains(
                station_name
            ), f"Missing travel time info for {station_name}"

    def set_parent_route(self, parent_route: "Route"):
        self.parent_route = parent_route

    @cached_property
    @listify
    def station_names(self):
        seen = set()
        for station_name_or_defn in self.stations:
            if isinstance(station_name_or_defn, str):
                name = station_name_or_defn
            else:
                name = station_name_or_defn.name
            assert (
                name not in seen
            ), f"Encountered non-unique station name {name} in list of stations for scheduler"
            seen.add(name)
            yield name


@dataclass
class Route(object):
    name: str
    id: str
    route_patterns: List[RoutePattern]
    trainset: Trainset = None
    directions: Tuple[str, str] = None
    shadows_real_route: str = None
    amenities: Amenities = field(default_factory=Amenities)
