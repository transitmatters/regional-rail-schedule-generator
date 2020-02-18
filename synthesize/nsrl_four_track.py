import network

from .stations import (
    create_four_track_station,
    create_two_track_station,
    create_network_from_routes_and_real_network,
)
from .routes import ALL_ROUTES

real_network = network.get_gtfs_network()

north_station = create_four_track_station(
    name="North Station",
    id="place-north",
    location=real_network.get_station_by_name("North Station").location,
)
south_station = create_four_track_station(
    name="South Station",
    id="place-sstat",
    location=real_network.get_station_by_name("South Station").location,
)


synth_network = create_network_from_routes_and_real_network(
    [north_station, south_station], ALL_ROUTES, real_network
)

print(synth_network.stations_by_id.values())
