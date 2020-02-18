from network import get_gtfs_network
from network.models import Network


def get_exemplar_trip_for_route(network: Network, route_id: str):
    return next(
        (trip for trip in network.trips_by_id.values() if trip.route_id == route_id),
        None,
    )


network = get_gtfs_network()
print(get_exemplar_trip_for_route(network, "CR-Franklin").stop_times[3].stop.parent_station.child_stops)
