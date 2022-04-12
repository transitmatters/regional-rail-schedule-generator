from network.time import time_seconds_to_string
from network.main import get_gtfs_network
from synthesize.distance import estimate_route_timetable
from scenarios.regional_rail.trainset import emu_trainset

real_network = get_gtfs_network()

stations = (
    "North Station",
    "Chelsea",
    "River Works",
    "Lynn",
    "Swampscott",
    "Salem",
    "Beverly",
    "North Beverly",
    "Hamilton/Wenham",
    "Ipswich",
    "Rowley",
    "Newburyport",
)

timetable = estimate_route_timetable(
    stations,
    real_network,
    emu_trainset,
)

for station in stations:
    travel_time_seconds = timetable.get_travel_time("North Station", station)
    print(station, time_seconds_to_string(travel_time_seconds))
