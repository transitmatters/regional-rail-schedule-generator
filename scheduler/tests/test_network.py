from scheduler.network import create_scheduler_network, get_key_stations
from scheduler.tests.data import route_patterns, trains_per_hour, X, Y, Z


def test_get_key_stations():
    all_stations = set(X.stations + Y.stations + Z.stations)
    unimportant_stations = set(("b", "e"))
    assert all_stations - unimportant_stations == get_key_stations(route_patterns)


def test_create_scheduler_network():
    sn = create_scheduler_network(route_patterns, trains_per_hour)
    assert set(node.station_name for node in sn.nodes.values()) == get_key_stations(route_patterns)
