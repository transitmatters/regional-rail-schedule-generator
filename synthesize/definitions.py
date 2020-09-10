from dataclasses import dataclass
from typing import Callable, Dict, List, Tuple, Union
from datetime import timedelta

from network.models import Network, Service
from network.time import DAYS_OF_WEEK
from synthesize.trainset import Trainset


def Time(hours, minutes):
    return timedelta(hours=hours, minutes=minutes)


@dataclass
class EvalContext(object):
    network: Network
    trainset: Trainset
    estimate_travel_time: Callable[..., int]


@dataclass
class Branching(object):
    shared_station_names: List[str]
    branch_station_names: List[Union[List[str], "Branching"]]


@dataclass
class Direction(object):
    name: str
    destination: str


@dataclass
class Route(object):
    name: str
    id: str
    shadows_real_route: Union[bool, str]
    stations: Union[List[str], Branching]
    schedule: "Schedule"
    directions: Tuple[Direction, Direction]


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
