from synthesize.definitions import Route, RoutePattern
from synthesize.routes import HAVERHILL, LOWELL
from synthesize.time import all_day_frequencies, Timetable

timetable = Timetable(
    {
        "North Station": "0:00",
        "West Medford": "0:13",
        "Wedgemere": "0:16",
        "Winchester Center": "0:18",
        "Anderson/Woburn": "0:25",
        "Wilmington": "0:30",
        "North Billerica": "0:38",
        "Lowell": "0:46",
        # Haverhill
        "Ballardvale": "0:47",
        "Andover": "0:53",
        "Lawrence": "1:00",
        "Bradford": "1:09",
        "Haverhill": "1:11",
    }
)

lowell = Route(
    id="CR-Lowell",
    shadows_real_route="CR-Lowell",
    name="Lowell Line",
    route_patterns=[
        RoutePattern(
            id="lowell",
            name="Lowell",
            stations=LOWELL,
            timetable=timetable,
            schedule=all_day_frequencies(30),
        )
    ],
)

haverhill = Route(
    id="CR-Haverhill",
    shadows_real_route="CR-Haverhill",
    name="Haverhill Line",
    route_patterns=[
        RoutePattern(
            id="haverhill",
            name="Haverhill",
            stations=HAVERHILL,
            timetable=timetable,
            schedule=all_day_frequencies(30),
        )
    ],
)
