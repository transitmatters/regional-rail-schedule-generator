from synthesize.definitions import Branching, Route, Weekdays, Saturday, Sunday, Station
from synthesize.routes import (
    EASTERN_SHARED,
    EASTERN_NEWBURYPORT,
    EASTERN_ROCKPORT,
    FAIRMOUNT,
    FRAMINGHAM_WORCESTER
)
from synthesize.trainset import Trainset
from synthesize.evaluate import evaluate_scenario
from synthesize.util import infill
from synthesize.write_gtfs import write_scenario_gtfs


def all_day_frequencies(headway):
    day_schedule = {  "05:00-23:59": headway }
    return {
        Weekdays: day_schedule,
        Saturday: day_schedule,
        Sunday: day_schedule,
    }

all_day_15 = all_day_frequencies(15)

station_north_revere = Station(
    name="Revere",
    id="place-rr-north-revere",
    location=(42.4154533, -70.9922548),
    municipality="Revere",
)

station_south_salem = Station(
    name="South Salem",
    id="place-rr-south-salem",
    location=(42.5073423, -70.8966044),
    municipality="Salem",
)

station_ceylon_park = Station(
    name="Ceylon Park",
    id="place-rr-ceylon-park",
    location=(42.3097728, -71.0735888),
    municipality="Boston",
)

station_river_street = Station(
    name="River Street",
    id="place-rr-river-street",
    location=(42.2637601, -71.1045547),
    municipality="Boston",
)

infill_stations = [
    station_north_revere,
    station_south_salem,
    station_ceylon_park,
    station_river_street,
]

eastern = Route(
    name="Newburyport/Rockport Line",
    id="CR-Newburyport",
    shadows_real_route="CR-Newburyport",
    stations=Branching(
        shared_station_names=infill(
            EASTERN_SHARED,
            ["Chelsea", station_north_revere, "River Works"],
            ["Swampscott", station_south_salem, "Salem"],
        ),
        branch_station_names=[EASTERN_NEWBURYPORT, EASTERN_ROCKPORT],
    ),
    travel_times={
        "North Station": "0:00",
        "Chelsea": "0:08",
        "Revere": "0:11",
        "River Works": "0:16",
        "Lynn": "0:18",
        "Swampscott": "0:20",
        "South Salem": "0:24",
        "Salem": "0:26",
        "Beverly": "0:28",
        # Rockport branch
        "Montserrat": "0:30",
        "Prides Crossing": "0:33",
        "Beverly Farms": "0:35",
        "Manchester": "0:38",
        "West Gloucester": "0:42",
        "Gloucester": "0:45",
        "Rockport": "0:49",
        # Newburyport branch
        "North Beverly": "0:31",
        "Hamilton/Wenham": "0:33",
        "Ipswich": "0:38",
        "Rowley": "0:41",
        "Newburyport": "0:47",
    },
    directions=["Outbound", "Inbound"],
    schedule=all_day_15,
)

fairmount = Route(
    name="Fairmount Line",
    id="CR-Fairmount",
    shadows_real_route="CR-Fairmount",
    stations=infill(
        FAIRMOUNT,
        ["Uphams Corner", station_ceylon_park, "Four Corners/Geneva"],
        ["Blue Hill Avenue", station_river_street, "Fairmount"],
    ),
    directions=["Outbound", "Inbound"],
    travel_times={
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
    },
    schedule=all_day_15,
)

worcester = Route(
    name="Worcester Line"
    id="CR-Worcester"
    shadows_real_route="CR-Worcester",
    stations=WORCESTER
)

routes = [eastern, fairmount]

trainset = Trainset(
    max_acceleration_kms2=6.67e-4,
    max_decceleration_kms2=8.88e-4,
    max_velocity_kms=129,
    dwell_time_seconds=45,
)

scenario = evaluate_scenario([eastern, fairmount], trainset, infill_stations)
write_scenario_gtfs(scenario, "gtfs-phase-one")
