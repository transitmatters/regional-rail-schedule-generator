from synthesize.definitions import Route, RoutePattern
from synthesize.routes import READING
from synthesize.time import all_day_frequencies, Timetable

timetable = Timetable(
    {
        "North Station": "0:00",
        "Malden Center": "0:11",
        "Wyoming Hill": "0:14",
        "Melrose Cedar Park": "0:16",
        "Melrose Highlands": "0:19",
        "Greenwood": "0:22",
        "Wakefield": "0:26",
        "Reading": "0:32",
    }
)

reading = Route(
    id="CR-Reading",
    shadows_real_route="CR-Haverhill",
    name="Reading Line",
    route_patterns=[
        RoutePattern(
            id="reading",
            name="Reading",
            stations=READING,
            timetable=timetable,
            schedule=all_day_frequencies(30),
        )
    ],
)
