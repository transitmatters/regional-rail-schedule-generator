from synthesize.definitions import Route, RoutePattern
from synthesize.time import Timetable, all_day_5

timetable = Timetable(
    {
        "Lynn": "0:00",
        "River Works": "0:02",
        "Wonderland": "0:04",
        "Revere Beach": "0:06",
        "Beachmont": "0:08",
        "Suffolk Downs": "0:10",
        "Orient Heights": "0:11",
        "Wood Island": "0:13",
        "Airport": "0:15",
        "Maverick": "0:16",
        "Aquarium": "0:18",
        "State": "0:20",
        "Government Center": "0:21",
        "Bowdoin": "0:23",
        "Charles/MGH": "0:24",
    }
)

stations = (
    "Lynn",
    "River Works",
    "Wonderland",
    "Revere Beach",
    "Beachmont",
    "Suffolk Downs",
    "Orient Heights",
    "Wood Island",
    "Airport",
    "Maverick",
    "Aquarium",
    "State",
    "Government Center",
    "Bowdoin",
    "Charles/MGH",
)

blue = Route(
    id="Blue",
    shadows_real_route="Blue",
    name="Blue Line",
    route_patterns=[
        RoutePattern(
            id="blue",
            name="Blue",
            stations=stations,
            timetable=timetable,
            schedule=all_day_5,
        )
    ],
)
