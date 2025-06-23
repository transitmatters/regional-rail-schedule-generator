from synthesize.definitions import Route, RoutePattern
from synthesize.time import Timetable, peak_offpeak_frequencies
from scenarios.expansion.infill_stations import (
    station_millennium_park,
)

timetable = Timetable(
    {
        "Oak Grove": "0:00",
        "Malden Center": "0:01",
        "Wellington": "0:05",
        "Assembly": "0:07",
        "Sullivan Square": "0:09",
        "Community College": "0:11",
        "North Station": "0:13",
        "Haymarket": "0:14",
        "State": "0:16",
        "Downtown Crossing": "0:17",
        "Chinatown": "0:18",
        "Tufts Medical Center": "0:19",
        "Back Bay": "0:21",
        "Massachusetts Avenue": "0:23",
        "Ruggles": "0:25",
        "Roxbury Crossing": "0:27",
        "Jackson Square": "0:29",
        "Stony Brook": "0:31",
        "Green Street": "0:32",
        "Forest Hills": "0:34",
        "Roslindale Village": "0:38",
        "Bellevue": "0:41",
        "Highland": "0:42",
        "West Roxbury": "0:43",
        "Millennium Park": "0:47",
        "Hersey": "0:51",
        "Needham Junction": "0:53",
    }
)

stations = (
    "Oak Grove",
    "Malden Center",
    "Wellington",
    "Assembly",
    "Sullivan Square",
    "Community College",
    "North Station",
    "Haymarket",
    "State",
    "Downtown Crossing",
    "Chinatown",
    "Tufts Medical Center",
    "Back Bay",
    "Massachusetts Avenue",
    "Ruggles",
    "Roxbury Crossing",
    "Jackson Square",
    "Stony Brook",
    "Green Street",
    "Forest Hills",
    "Roslindale Village",
    "Bellevue",
    "Highland",
    "West Roxbury",
    station_millennium_park,
    "Hersey",
    "Needham Junction"
)

orange = Route(
    id="Orange",
    shadows_real_route="Orange",
    name="Orange Line",
    route_patterns=[
        RoutePattern(
            id="orange",
            name="Orange",
            stations=stations,
            timetable=timetable,
            schedule=peak_offpeak_frequencies(4, 6),
        )
    ],
)
