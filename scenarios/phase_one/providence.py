from synthesize.definitions import Route, RoutePattern
from synthesize.routes import (
    PROVIDENCE_STOUGHTON_SHARED,
    PROVIDENCE,
    STOUGHTON,
    WICKFORD_JUNCTION,
)
from synthesize.time import Timetable, all_day_frequencies, peak_offpeak_frequencies
from synthesize.infill import infill

from scenarios.phase_one.infill_stations import station_pawtucket
from scenarios.phase_one.trainset import emu_trainset

timetable = Timetable(
    {
        "South Station": "0:00",
        "Back Bay": "0:04",
        "Ruggles": "0:06",
        "Forest Hills": "0:09",
        "Hyde Park": "0:13",
        "Readville": "0:15",
        "Route 128": "0:18",
        "Canton Junction": "0:21",
        # Stoughton branch
        "Canton Center": "0:23",
        "Stoughton": "0:26",
        # Providence branch
        "Sharon": "0:24",
        "Mansfield": "0:30",
        "Attleboro": "0:36",
        "South Attleboro": "0:41",
        "Pawtucket": "0:44",
        "Providence": "0:47",
        "TF Green Airport": "1:02",
        "Wickford Junction": "1:13",
    }
)

providence_stations = PROVIDENCE_STOUGHTON_SHARED + infill(
    PROVIDENCE, ["South Attleboro", station_pawtucket, "Providence"]
)

stoughton = RoutePattern(
    id="stoughton",
    stations=PROVIDENCE_STOUGHTON_SHARED + STOUGHTON,
    timetable=timetable,
    schedule=peak_offpeak_frequencies(15, 30),
)

providence = RoutePattern(
    id="providence",
    stations=providence_stations,
    timetable=timetable,
    schedule=all_day_frequencies(30),
)

wickford_junction = RoutePattern(
    id="wickford-junction",
    stations=providence_stations + WICKFORD_JUNCTION,
    timetable=timetable,
    schedule=all_day_frequencies(30),
)

providence_stoughton = Route(
    name="Providence/Stoughton Line",
    id="CR-Providence",
    shadows_real_route="CR-Providence",
    route_patterns=[stoughton, providence, wickford_junction],
    trainset=emu_trainset,
)
