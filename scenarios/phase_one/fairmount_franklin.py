from synthesize.definitions import Route, RoutePattern
from synthesize.routes import FAIRMOUNT
from synthesize.infill import infill
from synthesize.time import all_day_15, Timetable

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
        "Readville": "0:20",
    }
)

station_names = infill(
    FAIRMOUNT,
    ["Uphams Corner", station_ceylon_park, "Four Corners/Geneva"],
    ["Blue Hill Avenue", station_river_street, "Fairmount"],
)

fairmount_rp = RoutePattern(
    id="fairmount-0",
    stations=station_names,
    timetable=timetable,
    schedule=all_day_15,
)

fairmount = Route(
    name="Fairmount Line",
    id="CR-Fairmount",
    shadows_real_route="CR-Fairmount",
    route_patterns=[fairmount_rp],
    trainset=emu_trainset,
)
