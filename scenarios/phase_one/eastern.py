from synthesize.definitions import Route, RoutePattern
from synthesize.routes import (
    EASTERN_SHARED,
    EASTERN_NEWBURYPORT,
    EASTERN_ROCKPORT,
)
from synthesize.infill import infill
from synthesize.time import all_day_15, Timetable

from scenarios.phase_one.infill_stations import (
    station_north_revere,
    station_south_salem,
)
from scenarios.phase_one.trainset import emu_trainset

timetable = Timetable(
    {
        "North Station": "0:00",
        "Chelsea": "0:08",
        "Revere": "0:11",
        "River Works": "0:16",
        "Lynn": "0:18",
        "Swampscott": "0:20",
        "South Salem": "0:24",
        "Salem": "0:26",
        "Beverly": "0:28",
        # Rockport branch
        "Montserrat": "0:30",
        "Prides Crossing": "0:33",
        "Beverly Farms": "0:35",
        "Manchester": "0:38",
        "West Gloucester": "0:42",
        "Gloucester": "0:45",
        "Rockport": "0:49",
        # Newburyport branch
        "North Beverly": "0:31",
        "Hamilton/Wenham": "0:33",
        "Ipswich": "0:38",
        "Rowley": "0:41",
        "Newburyport": "0:47",
    }
)

shared_station_names = infill(
    EASTERN_SHARED,
    ["Chelsea", station_north_revere, "River Works"],
    ["Swampscott", station_south_salem, "Salem"],
)

newburyport = RoutePattern(
    name="Newburyport",
    id="newburyport",
    stations=(shared_station_names + EASTERN_NEWBURYPORT),
    timetable=timetable,
    schedule=all_day_15,
)

rockport = RoutePattern(
    name="Rockport",
    id="rockport",
    stations=(shared_station_names + EASTERN_ROCKPORT),
    timetable=timetable,
    schedule=all_day_15,
)

eastern = Route(
    name="Newburyport/Rockport",
    id="CR-Newburyport",
    shadows_real_route="CR-Newburyport",
    patterns=[newburyport, rockport],
    trainset=emu_trainset,
)
