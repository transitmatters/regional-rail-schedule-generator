from synthesize.write_gtfs import BUNDLE_COLUMNS, prune_bundle


def _trip(trip_id, route_id="CR-Worcester", service_id="weekday"):
    return {"route_id": route_id, "service_id": service_id, "trip_id": trip_id, "trip_headsign": "Boston"}


def _stop_time(trip_id, stop_id):
    return {"trip_id": trip_id, "arrival_time": "08:00:00", "stop_id": stop_id, "stop_sequence": "1"}


def _stop(stop_id, location_type="0", parent_station="place-sstat"):
    return {"stop_id": stop_id, "location_type": location_type, "parent_station": parent_station}


def _transfer(from_stop_id, to_stop_id):
    return {"from_stop_id": from_stop_id, "to_stop_id": to_stop_id, "min_transfer_time": "180"}


def _bundle():
    return {
        "stop_times.txt": [_stop_time("cr", "NEC-2287")],
        "calendar.txt": [{"service_id": "weekday", "monday": "1"}],
        "routes.txt": [{"route_id": "CR-Worcester"}, {"route_id": "Shuttle-Generic"}],
        "route_patterns.txt": [{"route_pattern_id": "CR-Worcester-0", "route_id": "CR-Worcester"}],
        "trips.txt": [
            _trip("cr"),
            _trip("holiday", service_id="ThanksgivingDay"),
            _trip("shuttle", route_id="Shuttle-Generic"),
            _trip("bus", route_id="1"),
        ],
        "relevant_stop_times.txt": [
            _stop_time("cr", "NEC-2287"),
            _stop_time("holiday", "NEC-2287"),
            _stop_time("shuttle", "shuttle-stop"),
        ],
        "stops.txt": [
            _stop("place-sstat", location_type="1", parent_station=""),
            _stop("place-bus-only", location_type="1", parent_station=""),
            _stop("NEC-2287"),
            _stop("shuttle-stop"),
            _stop("bus-stop", parent_station=""),
            _stop("door-sstat-atlantic", location_type="2"),
        ],
        "transfers.txt": [_transfer("NEC-2287", "place-sstat"), _transfer("NEC-2287", "bus-stop")],
    }


def test_drops_files_rre_does_not_read():
    pruned = prune_bundle(_bundle())
    assert "stop_times.txt" not in pruned
    assert set(pruned) <= set(BUNDLE_COLUMNS)


def test_drops_shuttle_holiday_and_unserved_trips():
    pruned = prune_bundle(_bundle())
    assert [row["trip_id"] for row in pruned["trips.txt"]] == ["cr"]
    assert [row["trip_id"] for row in pruned["relevant_stop_times.txt"]] == ["cr"]
    assert [row["route_id"] for row in pruned["routes.txt"]] == ["CR-Worcester"]


def test_keeps_every_station_but_only_served_stops():
    pruned = prune_bundle(_bundle())
    assert [row["stop_id"] for row in pruned["stops.txt"]] == ["place-sstat", "place-bus-only", "NEC-2287"]
    assert pruned["transfers.txt"] == [_transfer("NEC-2287", "place-sstat")]
