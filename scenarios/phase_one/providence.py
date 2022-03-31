from synthesize.definitions import Route, RoutePattern
from synthesize.time import Timetable, all_day_30, peak_offpeak_frequencies

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

shared_stations = (
    "South Station",
    "Back Bay",
    "Ruggles",
    "Forest Hills",
    "Hyde Park",
    "Readville",
    "Route 128",
    "Canton Junction",
)

providence_stations = (
    "Sharon",
    "Mansfield",
    "Attleboro",
    "South Attleboro",
    station_pawtucket,
    "Providence",
)

stoughton_stations = (
    "Canton Center",
    "Stoughton",
)

wickford_junction_stations = (
    "TF Green Airport",
    "Wickford Junction",
)


stoughton = RoutePattern(
    id="stoughton",
    stations=(shared_stations + stoughton_stations),
    timetable=timetable,
    schedule=peak_offpeak_frequencies(15, 30),
)


providence = RoutePattern(
    id="providence",
    stations=(shared_stations + providence_stations),
    timetable=timetable,
    schedule=all_day_30,
)

wickford_junction = RoutePattern(
    id="wickford-junction",
    stations=(providence_stations + wickford_junction_stations),
    timetable=timetable,
    schedule=all_day_30,
)

providence_stoughton = Route(
    name="Providence/Stoughton Line",
    id="CR-Providence",
    shadows_real_route="CR-Providence",
    route_patterns=[stoughton, providence, wickford_junction],
    trainset=emu_trainset,
)
