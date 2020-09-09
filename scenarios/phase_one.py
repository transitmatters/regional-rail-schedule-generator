from network.main import get_gtfs_network
from network.models import Service
from network.time import DAYS_OF_WEEK
from synthesize.network import create_synthetic_network
from synthesize.definitions import (
    EvalContext,
    Schedule,
    Service,
    Branching,
    Route,
    Time as T,
)
from synthesize.naive_scheduler import eval_route
from synthesize.routes import EASTERN_SHARED, EASTERN_NEWBURYPORT, EASTERN_ROCKPORT
from synthesize.trainset import Trainset

eastern = Route(
    name="Newburyport/Rockport",
    id="CR-Newburyport",
    shadows_real_route="CR-Newburyport",
    stations=Branching(
        shared_station_names=EASTERN_SHARED,
        branch_station_names=[EASTERN_NEWBURYPORT, EASTERN_ROCKPORT],
    ),
    directions=["Outbound", "Inbound"],
    schedule=Schedule(weekday={(T(5, 30), T(8, 30)): 15,}, saturday={}, sunday={}),
)


routes = [eastern]
real_network = get_gtfs_network()
network = create_synthetic_network(
    real_network=real_network, routes=routes, stations=[]
)
ctx = EvalContext(
    network=network,
    real_network=real_network,
    trainset=Trainset(
        max_acceleration_kms2=6.67e-4,
        max_decceleration_kms2=8.88e-4,
        max_velocity_kms=129,
        dwell_time_seconds=45,
    ),
    # TODO: Redesign this so we're not using Service objects directly here
    weekday_service=Service(id="weekday", days=DAYS_OF_WEEK[0:5]),
)
trips = eval_route(eastern, ctx)
