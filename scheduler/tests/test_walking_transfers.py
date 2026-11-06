from synthesize.walking_transfers import get_walking_transfer_rows


def _station(station_id):
    return {"stop_id": station_id, "location_type": "1", "parent_station": ""}


def _platform(stop_id, station_id):
    return {"stop_id": stop_id, "location_type": "0", "parent_station": station_id}


def _walk(place1, place2, distance_mi=0.3, duration_s=360, wheelchair_boarding=(1, 1)):
    return {
        "place1": place1,
        "place2": place2,
        "wheelchair_boarding_1": wheelchair_boarding[0],
        "wheelchair_boarding_2": wheelchair_boarding[1],
        "distance_mi": distance_mi,
        "duration_s": duration_s,
    }


STOPS = [
    _station("place-lansd"),
    _platform("lansd-1", "place-lansd"),
    _platform("lansd-2", "place-lansd"),
    _station("place-kencl"),
    _platform("kencl-1", "place-kencl"),
    {"stop_id": "kencl-entrance", "location_type": "2", "parent_station": "place-kencl"},
]


def _pairs(rows):
    return {(row["from_stop_id"], row["to_stop_id"]) for row in rows}


def test_links_every_platform_both_ways_with_a_buffer():
    rows = get_walking_transfer_rows(STOPS, [], [_walk("place-lansd", "place-kencl")])
    assert _pairs(rows) == {
        ("lansd-1", "kencl-1"),
        ("lansd-2", "kencl-1"),
        ("kencl-1", "lansd-1"),
        ("kencl-1", "lansd-2"),
    }
    assert {row["min_transfer_time"] for row in rows} == {"480"}


def test_skips_walks_that_are_too_long_or_not_step_free():
    walks = [
        _walk("place-lansd", "place-kencl", distance_mi=0.5),
        _walk("place-lansd", "place-kencl", wheelchair_boarding=(1, 2)),
        _walk("place-lansd", "place-kencl", wheelchair_boarding=(0, 1)),
    ]
    assert get_walking_transfer_rows(STOPS, [], walks) == []


def test_skips_stations_not_in_the_bundle_and_existing_transfers():
    existing = [{"from_stop_id": "lansd-1", "to_stop_id": "kencl-1", "min_transfer_time": "300"}]
    walks = [_walk("place-lansd", "place-kencl"), _walk("place-lansd", "place-dudly")]
    rows = get_walking_transfer_rows(STOPS, existing, walks)
    assert ("lansd-1", "kencl-1") not in _pairs(rows)
    assert len(rows) == 3
