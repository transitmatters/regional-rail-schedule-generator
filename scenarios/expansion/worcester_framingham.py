from synthesize.definitions import Route, RoutePattern
from synthesize.time import all_day_15, peak_offpeak_frequencies, Timetable

from scenarios.regional_rail.trainset import emu_trainset
from scenarios.regional_rail.infill_stations import (
    station_newton_corner,
    station_west_station,
)

framingham_stations = (
    "South Station",
    "Back Bay",
    "Lansdowne",
    station_west_station,
    "Boston Landing",
    station_newton_corner,
    "Newtonville",
    "West Newton",
    "Auburndale",
    "Wellesley Farms",
    "Wellesley Hills",
    "Wellesley Square",
    "Natick Center",
    "West Natick",
    "Framingham",
)

worcester_stations = (
    "South Station",
    "Back Bay",
    "Lansdowne",
    station_west_station,
    "Framingham",
    "Ashland",
    "Southborough",
    "Westborough",
    "Grafton",
    "Worcester",
)

framingham_timetable = Timetable(
    {
        "South Station": "0:00",
        "Back Bay": "0:03",
        "Lansdowne": "0:05",
        "West Station": "0:08",
        "Boston Landing": "0:10",
        "Newton Corner": "0:13",
        "Newtonville": "0:15",
        "West Newton": "0:17",
        "Auburndale": "0:19",
        "Wellesley Farms": "0:22",
        "Wellesley Hills": "0:24",
        "Wellesley Square": "0:26",
        "Natick Center": "0:30",
        "West Natick": "0:32",
        "Framingham": "0:35",
    }
)

worcester_timetable = Timetable(
    {
        "South Station": "0:00",
        "Back Bay": "0:03",
        "Lansdowne": "0:05",
        "West Station": "0:07",
        "Framingham": "0:21",
        "Ashland": "0:25",
        "Southborough": "0:29",
        "Westborough": "0:33",
        "Grafton": "0:38",
        "Worcester": "0:45",
    }
)

framingham = RoutePattern(
    name="Framingham",
    id="framingham",
    stations=framingham_stations,
    timetable=framingham_timetable,
    schedule=all_day_15,
)

worcester = RoutePattern(
    name="Worcester",
    id="worcester",
    stations=worcester_stations,
    timetable=worcester_timetable,
    schedule=peak_offpeak_frequencies(15, 30),
)

worcester_framingham = Route(
    name="Worcester/Framingham",
    id="CR-Worcester",
    shadows_real_route="CR-Worcester",
    trainset=emu_trainset,
    route_patterns=[framingham, worcester],
)
