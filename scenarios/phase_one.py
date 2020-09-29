from synthesize.definitions import Branching, Route, Time as T, Weekdays
from synthesize.routes import EASTERN_SHARED, EASTERN_NEWBURYPORT, EASTERN_ROCKPORT, FAIRMOUNT
from synthesize.trainset import Trainset
from synthesize.evaluate import evaluate_scenario
from synthesize.write_gtfs import write_scenario_gtfs

eastern = Route(
    name="Newburyport/Rockport",
    id="CR-Newburyport",
    shadows_real_route="CR-Newburyport",
    stations=Branching(
        shared_station_names=EASTERN_SHARED,
        branch_station_names=[EASTERN_NEWBURYPORT, EASTERN_ROCKPORT],
    ),
    directions=["Outbound", "Inbound"],
    schedule={
        Weekdays: {
            (T(5, 30), T(7, 00)): 15,
            (T(7, 00), T(10, 00)): 10,
            (T(10, 00), T(16, 30)): 15,
            (T(16, 30), T(19, 30)): 10,
            (T(19, 30), T(24, 00)): 15,
        }
    },
)

fairmount = Route(
    name="Fairmount",
    id="CR-Fairmount",
    shadows_real_route="CR-Fairmount",
    stations=FAIRMOUNT,
    directions=["Outbound", "Inbound"],
    schedule={
        Weekdays: {
            (T(5, 30), T(7, 00)): 15,
            (T(7, 00), T(10, 00)): 10,
            (T(10, 00), T(16, 30)): 15,
            (T(16, 30), T(19, 30)): 10,
            (T(19, 30), T(24, 00)): 15,
        }
    },
)

trainset = Trainset(
    max_acceleration_kms2=6.67e-4,
    max_decceleration_kms2=8.88e-4,
    max_velocity_kms=129,
    dwell_time_seconds=45,
)


scenario = evaluate_scenario([eastern, fairmount], trainset)
write_scenario_gtfs(scenario, "gtfs-phase-one")
