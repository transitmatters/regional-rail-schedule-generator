from synthesize.definitions import Route, RoutePattern
from synthesize.time import Timetable, peak_offpeak_frequencies
from scenarios.expansion.infill_stations import (
    station_bay_village,
    station_ink_block,
    station_reynolds,
    station_northampton,
    station_ramsay_park,
)


green_b_timetable = Timetable(
    {
        "Government Center": "0:00",
        "Park Street": "0:01",
        "Boylston": "0:03",
        "Arlington": "0:05",
        "Copley": "0:07",
        "Hynes Convention Center": "0:10",
        "Kenmore": "0:12",
        "Blandford Street": "0:14",
        "Boston University East": "0:15",
        "Boston University Central": "0:16",
        "Amory Street": "0:19",
        "Babcock Street": "0:21",
        "Packard's Corner": "0:23",
        "Harvard Avenue": "0:25",
        "Griggs Street": "0:26",
        "Allston Street": "0:27",
        "Warren Street": "0:28",
        "Washington Street": "0:30",
        "Sutherland Road": "0:31",
        "Chiswick Road": "0:33",
        "Chestnut Hill Avenue": "0:34",
        "South Street": "0:36",
        "Boston College": "0:39",
    }
)

green_c_timetable = Timetable(
    {
        "Government Center": "0:00",
        "Park Street": "0:01",
        "Boylston": "0:03",
        "Arlington": "0:05",
        "Copley": "0:07",
        "Hynes Convention Center": "0:10",
        "Kenmore": "0:12",
        "Saint Mary's Street": "0:15",
        "Hawes Street": "0:16",
        "Kent Street": "0:17",
        "Saint Paul Street": "0:18",
        "Coolidge Corner": "0:19",
        "Summit Avenue": "0:21",
        "Brandon Hall": "0:22",
        "Fairbanks Street": "0:23",
        "Washington Square": "0:24",
        "Tappan Street": "0:25",
        "Dean Road": "0:26",
        "Englewood Avenue": "0:28",
        "Cleveland Circle": "0:29",
    }
)

green_d_timetable = Timetable(
    {
        "Union Square": "0:00",
        "Lechmere": "0:03",
        "Science Park/West End": "0:05",
        "North Station": "0:07",
        "Haymarket": "0:09",
        "Government Center": "0:11",
        "Park Street": "0:13",
        "Boylston": "0:15",
        "Arlington": "0:17",
        "Copley": "0:19",
        "Hynes Convention Center": "0:21",
        "Kenmore": "0:23",
        "Fenway": "0:26",
        "Longwood": "0:28",
        "Brookline Village": "0:30",
        "Brookline Hills": "0:32",
        "Beaconsfield": "0:34",
        "Reservoir": "0:36",
        "Chestnut Hill": "0:38",
        "Newton Centre": "0:41",
        "Newton Highlands": "0:43",
        "Eliot": "0:45",
        "Waban": "0:47",
        "Woodland": "0:49",
        "Riverside": "0:51",
    }
)

green_e_timetable = Timetable(
    {
        "Medford/Tufts": "0:00",
        "Ball Square": "0:02",
        "Magoun Square": "0:04",
        "Gilman Square": "0:06",
        "East Somerville": "0:08",
        "Lechmere": "0:11",
        "Science Park/West End": "0:13",
        "North Station": "0:15",
        "Haymarket": "0:17",
        "Government Center": "0:19",
        "Park Street": "0:21",
        "Boylston": "0:23",
        "Arlington": "0:25",
        "Copley": "0:27",
        "Prudential": "0:29",
        "Symphony": "0:31",
        "Northeastern University": "0:33",
        "Museum of Fine Arts": "0:35",
        "Longwood Medical Area": "0:37",
        "Brigham Circle": "0:39",
        "Fenwood Road": "0:41",
        "Mission Park": "0:43",
        "Riverway": "0:45",
        "Back of the Hill": "0:47",
        "Heath Street": "0:49",
    }
)

green_f_timetable = Timetable(
    {
        "Government Center": "0:00",
        "Park Street": "0:02",
        "Boylston": "0:04",
        "Bay Village": "0:06",
        "Ink Block": "0:08",
        "Reynolds": "0:11",
        "Northampton": "0:14",
        "Ramsay Park": "0:16",
        "Nubian": "0:19",
    }
)

stations_shared = (
    "Government Center",
    "Park Street",
    "Boylston",
)

# TODO: Eventually we will map these to existing SL stops
stations_f_south = (
    station_bay_village,
    station_ink_block,
    station_reynolds,
    station_northampton,
    station_ramsay_park,
    "Nubian",
)

stations_e_north = (
    "Medford/Tufts",
    "Ball Square",
    "Magoun Square",
    "Gilman Square",
    "East Somerville",
    "Lechmere",
    "Science Park/West End",
    "North Station",
    "Haymarket",
)

stations_e_south = (
    "Arlington",
    "Copley",
    "Prudential",
    "Symphony",
    "Northeastern University",
    "Museum of Fine Arts",
    "Longwood Medical Area",
    "Brigham Circle",
    "Fenwood Road",
    "Mission Park",
    "Riverway",
    "Back of the Hill",
    "Heath Street",
)

stations_d_north = (
    "Union Square",
    "Lechmere",
    "Science Park/West End",
    "North Station",
    "Haymarket",
)

stations_d_south = (
    "Arlington",
    "Copley",
    "Hynes Convention Center",
    "Kenmore",
    "Fenway",
    "Longwood",
    "Brookline Village",
    "Brookline Hills",
    "Beaconsfield",
    "Reservoir",
    "Chestnut Hill",
    "Newton Centre",
    "Newton Highlands",
    "Eliot",
    "Waban",
    "Woodland",
    "Riverside",
)

stations_c_south = (
    "Arlington",
    "Copley",
    "Hynes Convention Center",
    "Kenmore",
    "Saint Mary's Street",
    "Hawes Street",
    "Kent Street",
    "Saint Paul Street",
    "Coolidge Corner",
    "Summit Avenue",
    "Brandon Hall",
    "Fairbanks Street",
    "Washington Square",
    "Tappan Street",
    "Dean Road",
    "Englewood Avenue",
    "Cleveland Circle",
)

stations_b_south = (
    "Arlington",
    "Copley",
    "Hynes Convention Center",
    "Kenmore",
    "Blandford Street",
    "Boston University East",
    "Boston University Central",
    "Amory Street",
    "Babcock Street",
    "Packard's Corner",
    "Harvard Avenue",
    "Griggs Street",
    "Allston Street",
    "Warren Street",
    "Washington Street",
    "Sutherland Road",
    "Chiswick Road",
    "Chestnut Hill Avenue",
    "South Street",
    "Boston College",
)

green_b = Route(
    id="Green-B",
    shadows_real_route="Green-B",
    name="Green Line B",
    route_patterns=[
        RoutePattern(
            id="green-b",
            name="Green B",
            stations=(stations_shared + stations_b_south),
            timetable=green_b_timetable,
            schedule=peak_offpeak_frequencies(7, 10),
        ),
    ],
)

green_c = Route(
    id="Green",
    shadows_real_route="Green-C",
    name="Green Line C",
    route_patterns=[
        RoutePattern(
            id="green-c",
            name="Green C",
            stations=(stations_shared + stations_c_south),
            timetable=green_c_timetable,
            schedule=peak_offpeak_frequencies(7, 10),
        ),
    ],
)

green_d = Route(
    id="Green",
    shadows_real_route="Green-D",
    name="Green Line D",
    route_patterns=[
        RoutePattern(
            id="green-d",
            name="Green D",
            stations=(stations_d_north + stations_shared + stations_d_south),
            timetable=green_d_timetable,
            schedule=peak_offpeak_frequencies(7, 10),
        ),
    ],
)

green_e = Route(
    id="Green-E",
    shadows_real_route="Green-E",
    name="Green Line E",
    route_patterns=[
        RoutePattern(
            id="green-e",
            name="Green E",
            stations=(stations_e_north + stations_shared + stations_e_south),
            timetable=green_e_timetable,
            schedule=peak_offpeak_frequencies(7, 10),
        ),
    ],
)

green_f = Route(
    id="Green-F",
    name="Green Line F",
    route_patterns=[
        RoutePattern(
            id="green-f",
            name="Green F",
            stations=(stations_shared + stations_f_south),
            timetable=green_f_timetable,
            schedule=peak_offpeak_frequencies(7, 10),
        ),
    ],
)
