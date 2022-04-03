from synthesize.definitions import Route, RoutePattern
from synthesize.time import Timetable, peak_offpeak_frequencies, all_day_30

from scenarios.regional_rail.infill_stations import (
    station_revere_center,
    station_south_salem,
    station_everett_jct,
)
from scenarios.regional_rail.trainset import emu_trainset

timetable = Timetable(
    {
        "North Station": "0:00",
        "Sullivan Square": "0:04",
        "S. Broadway/Everett Jct": "0:06",
        "Chelsea": "0:08",
        "Revere Center": "0:11",
        "Wonderland": "0:13",
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

shared_stations = (
    "North Station",
    station_everett_jct,
    "Sullivan Square",
    "Chelsea",
    station_revere_center,
    "Wonderland",
    "River Works",
    "Lynn",
    "Swampscott",
    station_south_salem,
    "Salem",
)

newburyport_stations = (
    "Beverly",
    "North Beverly",
    "Hamilton/Wenham",
    "Ipswich",
    "Rowley",
    "Newburyport",
)

rockport_stations = (
    "Beverly",
    "Montserrat",
    "Prides Crossing",
    "Beverly Farms",
    "Manchester",
    "West Gloucester",
    "Gloucester",
    "Rockport",
)

salem = RoutePattern(
    name="Salem",
    id="salem",
    stations=shared_stations,
    timetable=timetable,
    schedule=peak_offpeak_frequencies(15, 30),
)

newburyport = RoutePattern(
    name="Newburyport",
    id="newburyport",
    stations=(shared_stations + newburyport_stations),
    timetable=timetable,
    schedule=all_day_30,
)

rockport = RoutePattern(
    name="Rockport",
    id="rockport",
    stations=(shared_stations + rockport_stations),
    timetable=timetable,
    schedule=all_day_30,
)

eastern = Route(
    name="Newburyport/Rockport",
    id="CR-Newburyport",
    shadows_real_route="CR-Newburyport",
    route_patterns=[salem, newburyport, rockport],
    trainset=emu_trainset,
)
