from synthesize.definitions import Route, RoutePattern
from synthesize.routes import FRAMINGHAM, WORCESTER
from synthesize.infill import infill
from synthesize.time import all_day_15, peak_offpeak_frequencies, Timetable

from scenarios.phase_one.infill_stations import (
    station_newton_corner,
    station_west_station,
)

framingham_stations = infill(
    FRAMINGHAM,
    ["Lansdowne", station_west_station, "Boston Landing"],
    ["Boston Landing", station_newton_corner, "Newtonville"],
)

worcester_stations = infill(WORCESTER, ["Lansdowne", station_newton_corner, "Framingham"])

timetable = Timetable(
    {
        "South Station": "0:00",
        "Back Bay": "0:03",
        "Lansdowne": "0:05",
        "West Station": "0:08",
        "Boston Landing": "0:16",
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

express_timetable = Timetable(
    {
        "South Station": "0:00",
        "Back Bay": "0:03",
        "Lansdowne": "0:05",
        "Newton Corner": "0:10",
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
    timetable=timetable,
    schedule=all_day_15,
)

worcester = RoutePattern(
    name="Worcester",
    id="worcester",
    stations=worcester_stations,
    timetable=express_timetable,
    schedule=peak_offpeak_frequencies(15, 30),
)

worcester_framingham = Route(
    name="Worcester/Framingham",
    id="CR-Worcester",
    shadows_real_route="CR-Worcester",
    patterns=[framingham, worcester],
)
