from dataclasses import dataclass
from typing import List, Tuple, Dict, Union
from datetime import timedelta

from network.models import Network, Service
from synthesize.trainset import Trainset

Frequencies = Dict[Tuple[timedelta, timedelta], float]

def Time(hours, minutes):
    return timedelta(hours=hours, minutes=minutes)

@dataclass
class EvalContext(object):
    network: Network
    real_network: Network
    trainset: Trainset
    weekday_service: Service


@dataclass
class Schedule(object):
    weekday: Frequencies
    saturday: Frequencies
    sunday: Frequencies


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
    schedule: Schedule
    directions: Tuple[Direction, Direction]
