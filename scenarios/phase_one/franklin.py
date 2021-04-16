from synthesize.definitions import Route, RoutePattern
from synthesize.routes import FRANKLIN
from synthesize.time import Timetable, all_day_frequencies

timetable = Timetable(
    {
        "South Station": "0:00",
        "Back Bay": "0:06",
        "Ruggles": "0:10",
        "Readville": "0:20",
        "Endicott": "0:25",
        "Dedham Corp Center": "0:28",
        "Islington": "0:31",
        "Norwood Depot": "0:35",
        "Norwood Central": "0:38",
        "Windsor Gardens": "0:43",
        "Walpole": "0:47",
        "Norfolk": "0:54",
        "Franklin": "1:01",
        "Forge Park/495": "1:08",
    }
)

franklin = Route(
    id="CR-Franklin",
    shadows_real_route="CR-Franklin",
    name="Franklin Line",
    route_patterns=[
        RoutePattern(
            id="franklin",
            name="Franklin",
            stations=FRANKLIN,
            timetable=timetable,
            schedule=all_day_frequencies(30),
        )
    ],
)
