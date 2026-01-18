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
class InfillStation(Station):
    """
    A specialized Station class for infill stations that provides consistent ID prefixes
    based on the route type.
    
    Route types and their corresponding prefixes:
    - 'regional_rail': Regional Rail infill stations -> 'place-rr-'
    - 'green_line_extension': Green Line Extension -> 'place-glx-'
    - 'blue_line': Blue Line extensions -> 'place-blx-'
    - 'orange_line': Orange Line extensions -> 'place-olx-'
    - 'red_line': Red Line extensions -> 'place-rlx-'
    - 'silver_line': Silver Line extensions -> 'place-slx-'
    """
    route_type: str = "regional_rail"
    
    # Mapping of route types to their ID prefixes
    _PREFIX_MAP = {
        "regional_rail": "place-rr-",
        "green_line_extension": "place-glx-",
        "blue_line_extension": "place-blx-",
        "orange_line_extension": "place-olx-",
        "red_line_extension": "place-rlx-",
        "silver_line_extension": "place-slx-"
    }
    
    def __post_init__(self):
        # Get the prefix for this route type
        prefix = self._PREFIX_MAP.get(self.route_type, "place-rr-")

        # Convert station name to lowercase, replace spaces and special chars with hyphens
        station_slug = self.name.lower()
        station_slug = station_slug.replace(" ", "-").replace("/", "-").replace("'", "")
        station_slug = station_slug.replace("(", "").replace(")", "")
        station_slug = station_slug.replace(".", "")
        # Remove multiple consecutive hyphens
        while "--" in station_slug:
            station_slug = station_slug.replace("--", "-")
        # Remove leading/trailing hyphens
        station_slug = station_slug.strip("-")
        
        self.id = f"{prefix}{station_slug}"


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
            assert self.timetable.contains(station_name), f"Missing travel time info for {station_name}"

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
            assert name not in seen, f"Encountered non-unique station name {name} in list of stations for scheduler"
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
