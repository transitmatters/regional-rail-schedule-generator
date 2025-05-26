from synthesize.definitions import Route, RoutePattern
from synthesize.time import Timetable, peak_offpeak_frequencies

timetable = Timetable(
    {
        "Lynn": "0:00",
        "West Lynn": "0:02",
        "River Works": "0:05",
        "Wonderland": "0:10",
        "Revere Beach": "0:11",
        "Beachmont": "0:13",
        "Suffolk Downs": "0:15",
        "Orient Heights": "0:16",
        "Wood Island": "0:20",
        "Airport": "0:22",
        "Maverick": "0:24",
        "Aquarium": "0:26",
        "State": "0:27",
        "Government Center": "0:28",
        "Bowdoin": "0:29",
        "Charles/MGH": "0:30"
    }
)

stations = (
    "Lynn",
    "West Lynn",
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
    name="Blue Line (Charles/MGH + Lynn)",
    route_patterns=[
        RoutePattern(
            id="blue",
            name="Blue",
            stations=stations,
            timetable=timetable,
            schedule=peak_offpeak_frequencies(5, 7),
        )
    ],
)
