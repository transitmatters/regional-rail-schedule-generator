from synthesize.definitions import Route, RoutePattern
from synthesize.time import Timetable, peak_offpeak_frequencies
from scenarios.expansion.infill_stations import (
    station_arlington_heights,
    station_arlington_center,
)

timetable = Timetable(
    {
        "Arlington Heights": "0:00",
        "Arlington Center": "0:03",
        "Alewife": "0:06",
        "Davis": "0:08",
        "Porter": "0:10",
        "Harvard": "0:13",
        "Central": "0:17",
        "Kendall/MIT": "0:19",
        "Charles/MGH": "0:21",
        "Park Street": "0:23",
        "Downtown Crossing": "0:25",
        "South Station": "0:26",
        "Broadway": "0:28",
        "Andrew": "0:30",
        "JFK/UMass": "0:32",
        # Ashmont Branch
        "Savin Hill": "0:34",
        "Fields Corner": "0:37",
        "Shawmut": "0:39",
        "Ashmont": "0:42",
        # Braintree Branch
        "North Quincy": "0:39",
        "Wollaston": "0:41",
        "Quincy Center": "0:44",
        "Quincy Adams": "0:49",
        "Braintree": "0:53",
    }
)

stations_shared = (
    station_arlington_heights,
    station_arlington_center,
    "Alewife",
    "Davis",
    "Porter",
    "Harvard",
    "Central",
    "Kendall/MIT",
    "Charles/MGH",
    "Park Street",
    "Downtown Crossing",
    "South Station",
    "Broadway",
    "Andrew",
    "JFK/UMass",
)

stations_a = ("Savin Hill", "Fields Corner", "Shawmut", "Ashmont")

stations_b = ("North Quincy", "Wollaston", "Quincy Center", "Quincy Adams", "Braintree")

red = Route(
    id="Red",
    shadows_real_route="Red",
    name="Red Line",
    route_patterns=[
        RoutePattern(
            id="red-a",
            name="Red Ashmont",
            stations=(stations_shared + stations_a),
            timetable=timetable,
            schedule=peak_offpeak_frequencies(8, 10),
        ),
        RoutePattern(
            id="red-b",
            name="Red Braintree",
            stations=(stations_shared + stations_b),
            timetable=timetable,
            schedule=peak_offpeak_frequencies(8, 10),
        ),
    ],
)
