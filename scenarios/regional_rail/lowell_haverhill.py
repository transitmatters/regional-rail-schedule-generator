from synthesize.definitions import Route, RoutePattern
from synthesize.time import all_day_30, Timetable

from scenarios.regional_rail.infill_stations import (
    station_tufts_university,
    station_montvale_avenue,
    station_umass_lowell,
    station_rourke_bridge,
    station_willow_springs,
    station_nashua,
    station_merrimack,
    station_manchester_center,
)

timetable = Timetable(
    {
        "North Station": "0:00",
        "Tufts University": "0:05",
        "West Medford": "0:08",
        "Wedgemere": "0:10",
        "Winchester Center": "0:12",
        "Montvale Avenue": "0:15",
        "Mishawum": "0:17",
        "Anderson/Woburn": "0:19",
        "Wilmington": "0:22",
        # Haverhill
        "Ballardvale": "0:27",
        "Andover": "0:30",
        "Lawrence": "0:34",
        "Bradford": "0:39",
        "Haverhill": "0:40",
        # Lowell / NH
        "North Billerica": "0:27",
        "Lowell": "0:31",
        "UMass Lowell": "0:33",
        "Rourke Bridge": "0:35",
        "Willow Springs": "0:42",
        "Nashua": "0:46",
        "Merrimack": "0:52",
        "Manchester Center": "1:00",
    }
)

shared_stations = (
    "North Station",
    station_tufts_university,
    "West Medford",
    "Wedgemere",
    "Winchester Center",
    station_montvale_avenue,
    "Mishawum",
    "Anderson/Woburn",
    "Wilmington",
)


lowell_stations = (
    "North Billerica",
    "Lowell",
    station_umass_lowell,
    station_rourke_bridge,
    station_willow_springs,
    station_nashua,
    station_merrimack,
    station_manchester_center,
)

haverhill_stations = (
    "Ballardvale",
    "Andover",
    "Lawrence",
    "Bradford",
    "Haverhill",
)


lowell = Route(
    id="CR-Lowell",
    shadows_real_route="CR-Lowell",
    name="Lowell Line",
    route_patterns=[
        RoutePattern(
            id="lowell",
            name="Lowell",
            stations=(shared_stations + lowell_stations),
            timetable=timetable,
            schedule=all_day_30,
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
            stations=(shared_stations + haverhill_stations),
            timetable=timetable,
            schedule=all_day_30,
        )
    ],
)
