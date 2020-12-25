from dataclasses import dataclass
from typing import Callable, Dict, List, Tuple, Union
from datetime import timedelta

from network.models import Network, Service
from network.time import DAYS_OF_WEEK, parse_schedule_dict, parse_travel_time_dict
from synthesize.trainset import Trainset


@dataclass
class EvalContext(object):
    network: Network
    trainset: Trainset
    get_travel_time: Callable[..., int]


@dataclass
class Branching(object):
    shared_station_names: List[str]
    branch_station_names: List[Union[List[str], "Branching"]]


@dataclass
class Direction(object):
    name: str
    destination: str


class Route(object):
    def __init__(
        self,
        name: str,
        id: str,
        shadows_real_route: str,
        stations: Union[List[str], Branching],
        schedule: Dict[str, float],
        directions: Tuple[Direction, Direction],
        travel_times: Dict[str, str] = None,
    ):
        self.name = name
        self.id = id
        self.shadows_real_route = shadows_real_route
        self.stations = stations
        self.schedule = parse_schedule_dict(schedule)
        self.travel_times = parse_travel_time_dict(travel_times) if travel_times else None
        self.directions = directions


class Station(object):
    def __init__(self, name: str, id: str, location: Tuple[float, float], municipality):
        self.name = name
        self.id = id
        self.location = location
        self.municipality = municipality


Weekdays = Service(
    id="weekdays",
    days=DAYS_OF_WEEK[0:5],
    description="Weekdays",
    schedule_name="Weekdays",
    schedule_type="Weekday",
    schedule_typicality=4,
)

Saturday = Service(
    id="saturday",
    days=["saturday"],
    description="Saturday",
    schedule_name="Saturday",
    schedule_type="Saturday",
    schedule_typicality=4,
)

Sunday = Service(
    id="sunday",
    days=["sunday"],
    description="Sunday",
    schedule_name="Sunday",
    schedule_type="Sunday",
    schedule_typicality=4,
)

Frequencies = Dict[Tuple[timedelta, timedelta], float]
Schedule = Dict[Service, Frequencies]
