from synthesize.definitions import Route, RoutePattern
from synthesize.time import Timetable, all_day_30

timetable = Timetable(
    {
        "South Station": "0:00",
        "Back Bay": "0:05",
        "Ruggles": "0:08",
        "Forest Hills": "0:13",
        "Roslindale Village": "0:16",
        "Bellevue": "0:19",
        "Highland": "0:21",
        "West Roxbury": "0:23",
        "Hersey": "0:33",
        "Needham Junction": "0:36",
        "Needham Center": "0:39",
        "Needham Heights": "0:45",
    }
)

stations = (
    "South Station",
    "Back Bay",
    "Ruggles",
    "Forest Hills",
    "Roslindale Village",
    "Bellevue",
    "Highland",
    "West Roxbury",
    "Hersey",
    "Needham Junction",
    "Needham Center",
    "Needham Heights",
)

needham = Route(
    id="CR-Needham",
    shadows_real_route="CR-Needham",
    name="Needham Line",
    route_patterns=[
        RoutePattern(
            id="needham",
            name="Needham",
            stations=stations,
            timetable=timetable,
            schedule=all_day_30,
        )
    ],
)
