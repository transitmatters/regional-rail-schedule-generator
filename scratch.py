from network import get_gtfs_network
from synthesize.util import estimate_total_route_time
from synthesize.trainset import Trainset
from synthesize.routes import FRAMINGHAM_WORCESTER

trainset = Trainset(
    max_acceleration_kms2=6.67e-4, max_decceleration_kms2=8.88e-4, max_velocity_kms=129
)
network = get_gtfs_network()

print(estimate_total_route_time(FRAMINGHAM_WORCESTER, network, trainset) / 60)
