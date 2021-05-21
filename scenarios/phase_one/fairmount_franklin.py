from synthesize.definitions import Route, RoutePattern
from synthesize.routes import FAIRMOUNT, FRANKLIN_TO_FORGE_PARK, FRANKLIN_TO_NORWOOD
from synthesize.infill import infill
from synthesize.time import all_day_15, all_day_30, Timetable

from scenarios.phase_one.infill_stations import (
    station_ceylon_park,
    station_river_street,
)
from scenarios.phase_one.trainset import emu_trainset


timetable = Timetable(
    {
        "South Station": "0:00",
        "Newmarket": "0:05",
        "Uphams Corner": "0:07",
        "Ceylon Park": "0:09",
        "Four Corners/Geneva": "0:10",
        "Talbot Avenue": "0:11",
        "Morton Street": "0:13",
        "Blue Hill Avenue": "0:15",
        "River Street": "0:17",
        "Fairmount": "0:19",
        # Franklin
        "Readville": "0:20",
        "Endicott": "0:22",
        "Dedham Corp Center": "0:24",
        "Islington": "0:26",
        "Norwood Depot": "0:29",
        "Norwood Central": "0:31",
        "Windsor Gardens": "0:33",
        "Walpole": "0:37",
        "Norfolk": "0:41",
        "Franklin": "0:45",
        "Forge Park/495": "0:48",
    }
)

fairmount_station_names = infill(
    FAIRMOUNT,
    ["Uphams Corner", station_ceylon_park, "Four Corners/Geneva"],
    ["Blue Hill Avenue", station_river_street, "Fairmount"],
)


fairmount = Route(
    name="Fairmount Line",
    id="CR-Fairmount",
    shadows_real_route="CR-Fairmount",
    trainset=emu_trainset,
    route_patterns=[
        RoutePattern(
            id="fairmount",
            stations=fairmount_station_names,
            timetable=timetable,
            schedule=all_day_15,
        )
    ],
)

franklin = Route(
    id="CR-Franklin",
    shadows_real_route="CR-Franklin",
    name="Franklin Line",
    trainset=emu_trainset,
    route_patterns=[
        RoutePattern(
            id="franklin-norwood",
            name="Franklin/Norwood",
            stations=fairmount_station_names + FRANKLIN_TO_NORWOOD,
            timetable=timetable,
            schedule=all_day_30,
        ),
        RoutePattern(
            id="franklin-forge-park",
            name="Franklin/Forge Park",
            stations=fairmount_station_names + FRANKLIN_TO_NORWOOD + FRANKLIN_TO_FORGE_PARK,
            timetable=timetable,
            schedule=all_day_30,
        ),
    ],
)
