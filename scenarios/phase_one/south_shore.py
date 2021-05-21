from synthesize.definitions import Route, RoutePattern
from synthesize.routes import (
    GREENBUSH,
    OC_KINGSTON_PLYMOUTH,
    OC_MIDDLEBOROUGH_LAKEVILLE,
)
from synthesize.time import Timetable, all_day_30
from synthesize.infill import infill

from scenarios.phase_one.infill_stations import (
    station_braintree_highlands,
    station_bridgewater_center,
    station_cohasset_center,
    station_kingston_junction,
    station_middleborough_centre_st,
    station_plymouth_center,
    station_rockland_north_abington,
    station_weymouth_columbian_square,
)
from scenarios.phase_one.trainset import emu_trainset

timetable = Timetable(
    {
        "South Station": "0:00",
        "JFK/UMass": "0:04",
        "Quincy Center": "0:10",
        # Greenbush
        "Weymouth Landing/East Braintree": "0:16",
        "East Weymouth": "0:19",
        "West Hingham": "0:21",
        "Hingham Depot": "0:23",
        "Nantasket Junction": "0:25",
        "Cohasset Center": "0:29",
        "North Scituate": "0:32",
        "Greenbush": "0:36",
        # Middleborough/Lakeville
        "Braintree": "0:14",
        "Braintree Highlands": "0:16",
        "Holbrook/Randolph": "0:19",
        "Montello": "0:23",
        "Brockton": "0:25",
        "Campello": "0:28",
        "Bridgewater Center": "0:33",
        "Bridgewater": "0:34",
        "Middleborough Centre St": "0:40",
        "Middleborough/Lakeville": "0:42",
        # TODO(ian): Add Cape stations here?
        # Plymouth
        "Weymouth Columbian Square": "0:18",
        "South Weymouth": "0:20",
        "Rockland-North Abington": "0:23",
        "Abington": "0:26",
        "Whitman": "0:28",
        "Hanson": "0:32",
        "Halifax": "0:36",
        "Kingston Junction": "0:40",
        "Plymouth": "0:43",
        "Plymouth Center": "0:45",
    }
)

stations_greenbush = infill(
    GREENBUSH,
    ["Nantasket Junction", station_cohasset_center, "North Scituate"],
)

stations_middleborough_lakeville = infill(
    OC_MIDDLEBOROUGH_LAKEVILLE,
    ["Braintree", station_braintree_highlands, "Holbrook/Randolph"],
    ["Campello", station_bridgewater_center, "Bridgewater"],
    ["Bridgewater", station_middleborough_centre_st, "Middleborough/Lakeville"],
)

stations_plymouth = (
    *infill(
        OC_KINGSTON_PLYMOUTH,
        ["Braintree", station_weymouth_columbian_square, "South Weymouth"],
        ["South Weymouth", station_rockland_north_abington, "Abington"],
        ["Halifax", station_kingston_junction, "Plymouth"],
    ),
    station_plymouth_center,
)

greenbush = Route(
    id="CR-Greenbush",
    shadows_real_route="CR-Greenbush",
    name="Greenbush Line",
    trainset=emu_trainset,
    route_patterns=[
        RoutePattern(
            id="greenbush",
            name="Greenbush",
            timetable=timetable,
            stations=stations_greenbush,
            schedule=all_day_30,
        )
    ],
)

middleborough = Route(
    id="CR-Middleborough",
    shadows_real_route="CR-Middleborough",
    name="Middleborough/Lakeville Line",
    trainset=emu_trainset,
    route_patterns=[
        RoutePattern(
            id="middleborough-lakeville",
            name="Middleborough/Lakeville",
            timetable=timetable,
            stations=stations_middleborough_lakeville,
            schedule=all_day_30,
        )
    ],
)

plymouth = Route(
    id="CR-Plymouth",
    shadows_real_route="CR-Kingston",
    name="Plymouth Line",
    trainset=emu_trainset,
    route_patterns=[
        RoutePattern(
            id="plymouth",
            name="Plymouth",
            timetable=timetable,
            stations=stations_plymouth,
            schedule=all_day_30,
        )
    ],
)
