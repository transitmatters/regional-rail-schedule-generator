from synthesize.definitions import Route, RoutePattern
from synthesize.time import all_day_15, Timetable

timetable = Timetable(
    {
        "North Station": "0:00",
        "Sullivan Square": "0:04",
        "Malden Center": "0:07",
        "Wyoming Hill": "0:10",
        "Melrose/Cedar Park": "0:12",
        "Melrose Highlands": "0:13",
        "Greenwood": "0:15",
        "Wakefield": "0:17",
        "Reading": "0:20",
    }
)

stations = (
    "North Station",
    "Sullivan Square",
    "Malden Center",
    "Wyoming Hill",
    "Melrose/Cedar Park",
    "Melrose Highlands",
    "Greenwood",
    "Wakefield",
    "Reading",
)

reading = Route(
    id="CR-Reading",
    shadows_real_route="CR-Haverhill",
    name="Reading Line",
    route_patterns=[
        RoutePattern(
            id="reading",
            name="Reading",
            stations=stations,
            timetable=timetable,
            schedule=all_day_15,
        )
    ],
)
