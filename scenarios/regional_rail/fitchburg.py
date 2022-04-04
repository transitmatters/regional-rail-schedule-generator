from synthesize.definitions import Route, RoutePattern
from synthesize.time import Timetable, peak_offpeak_frequencies

from scenarios.regional_rail.infill_stations import (
    station_brickbottom,
    station_clematis_brook,
    station_weston_128,
)

timetable = Timetable(
    {
        "North Station": "0:00",
        "Brickbottom": "0:02",
        "Union Square": "0:04",
        "Porter": "0:06",
        "Alewife": "0:09",
        "Belmont": "0:11",
        "Waverley": "0:13",
        "Clematis Brook/Warrendale": "0:16",
        "Waltham": "0:17",
        "Brandeis/Roberts": "0:20",
        "Weston/128": "0:23",
        "Lincoln": "0:26",
        "Concord": "0:30",
        "West Concord": "0:32",
        "South Acton": "0:36",
        "Littleton/Route 495": "0:40",
        "Ayer": "0:46",
        "Shirley": "0:49",
        "North Leominster": "0:55",
        "Fitchburg": "0:59",
        "Wachusett": "1:03",
    }
)

shared_stations = (
    "North Station",
    station_brickbottom,
    "Union Square",
    "Porter",
    "Belmont",
    "Waverley",
    station_clematis_brook,
    "Waltham",
    "Brandeis/Roberts",
)

fitchburg_stations = (
    station_weston_128,
    "Lincoln",
    "Concord",
    "West Concord",
    "South Acton",
    "Littleton/Route 495",
    "Ayer",
    "Shirley",
    "North Leominster",
    "Fitchburg",
    "Wachusett",
)


fitchburg = Route(
    id="CR-Fitchburg",
    shadows_real_route="CR-Fitchburg",
    name="Fitchburg Line",
    route_patterns=[
        RoutePattern(
            id="brandeis",
            stations=shared_stations,
            schedule=peak_offpeak_frequencies(0, 30),
            timetable=timetable,
        ),
        RoutePattern(
            id="fitchburg",
            stations=(shared_stations + fitchburg_stations),
            schedule=peak_offpeak_frequencies(15, 30),
            timetable=timetable,
        ),
    ],
)
