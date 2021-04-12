from dataclasses import dataclass
from functools import cached_property
from typing import Dict, List, Tuple, Union
from datetime import timedelta

from numpy import isin

from network.models import Network, Service
from synthesize.time import Timetable
from synthesize.trainset import Trainset
from synthesize.util import listify

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

    @cached_property
    @listify
    def station_names(self):
        seen = set()
        for station_name_or_defn in self.stations:
            if isinstance(station_name_or_defn, str):
                name = station_name_or_defn
            else:
                name = station_name_or_defn.name
            if name in seen:
                raise Exception(
                    f"Encountered non-unique station name {name} in list of stations for scheduler"
                )
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
