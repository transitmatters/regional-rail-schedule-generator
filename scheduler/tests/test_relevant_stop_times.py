from network.relevant_stop_times import is_relevant_route_id


def test_rapid_transit_routes_are_relevant():
    for route_id in ("Red", "Orange", "Blue", "Green-B", "Green-E", "Mattapan"):
        assert is_relevant_route_id(route_id)


def test_commuter_rail_and_silver_line_are_relevant():
    assert is_relevant_route_id("CR-Worcester")
    assert is_relevant_route_id("741")


def test_buses_and_shuttles_are_not_relevant():
    assert not is_relevant_route_id("1")
    assert not is_relevant_route_id("Shuttle-AshmontMattapan")
