from synthesize.definitions import Route, RoutePattern
from synthesize.time import Timetable, peak_offpeak_frequencies
from scenarios.expansion.infill_stations import station_west_lynn

timetable = Timetable(
    {
        "Lynn": "0:00",
        "West Lynn": "0:03",
        "River Works": "0:05",
        "Wonderland": "0:10",
        "Revere Beach": "0:11",
        "Beachmont": "0:14",
        "Suffolk Downs": "0:15",
        "Orient Heights": "0:17",
        "Wood Island": "0:20",
        "Airport": "0:22",
        "Maverick": "0:24",
        "Aquarium": "0:27",
        "State": "0:28",
        "Government Center": "0:29",
        "Bowdoin": "0:30",
        "Charles/MGH": "0:31",
    }
)

stations = (
    "Lynn",
    station_west_lynn,
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
            schedule=peak_offpeak_frequencies(5, 7),
        )
    ],
)
