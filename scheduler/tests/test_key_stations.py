from scheduler.key_stations import get_key_stations
from scheduler.tests.data import route_patterns, X, Y, Z


def test_get_key_stations():
    all_stations = set(X.stations + Y.stations + Z.stations)
    unimportant_stations = set(("b", "e"))
    assert all_stations - unimportant_stations == get_key_stations(route_patterns)
