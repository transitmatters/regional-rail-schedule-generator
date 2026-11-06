"""Transfers that leave one station and walk to another nearby, like Lansdowne to Kenmore (RRE issue #58).

walking-distances.json is copied from https://github.com/transitmatters/station-walking-distance, which
looks up walking times from OpenStreetMap. Copy in a new version when stations open or move.
"""

import json
import os
from typing import Dict, List

from network.models import LocationType

WALKING_DISTANCES_FILE = os.path.join(os.path.dirname(__file__), "walking-distances.json")

# Walks longer than this rarely beat riding, and walking times grow less reliable. This is about the 0.4 mi
# cutoff first used with 2022 data that was rounded to tenths of a mile, so it keeps walks like Back Bay to Prudential.
MAX_WALK_MILES = 0.45

# The routed times are door to door for someone walking. Add time for elevators, fare gates and
# getting to the platform, and for people who move more slowly.
PLATFORM_ACCESS_BUFFER_S = 120

ACCESSIBLE = 1

Rows = List[Dict[str, str]]


def load_walking_distances() -> List[dict]:
    with open(WALKING_DISTANCES_FILE) as file:
        return list(json.load(file).values())


def is_usable_walk(walk: dict) -> bool:
    # Only include walks that work for wheelchair users, so every journey RRE plans stays step-free
    # when its stations are
    return (
        walk["distance_mi"] <= MAX_WALK_MILES
        and walk["wheelchair_boarding_1"] == ACCESSIBLE
        and walk["wheelchair_boarding_2"] == ACCESSIBLE
    )


def get_walking_transfer_rows(stop_rows: Rows, transfer_rows: Rows, walks: List[dict]) -> Rows:
    """Transfer rows between every platform of each pair of stations a short, step-free walk apart,
    in both directions. Skips stations not in stop_rows and transfers that already exist."""
    platforms_by_station: Dict[str, List[str]] = {}
    for row in stop_rows:
        if row["location_type"] == LocationType.STOP and row["parent_station"]:
            platforms_by_station.setdefault(row["parent_station"], []).append(row["stop_id"])
    existing = {(row["from_stop_id"], row["to_stop_id"]) for row in transfer_rows}
    rows = []
    for walk in walks:
        if not is_usable_walk(walk):
            continue
        min_transfer_time = str(walk["duration_s"] + PLATFORM_ACCESS_BUFFER_S)
        station_1, station_2 = walk["place1"], walk["place2"]
        for from_station, to_station in ((station_1, station_2), (station_2, station_1)):
            for from_stop_id in platforms_by_station.get(from_station, []):
                for to_stop_id in platforms_by_station.get(to_station, []):
                    if (from_stop_id, to_stop_id) in existing:
                        continue
                    existing.add((from_stop_id, to_stop_id))
                    rows.append(
                        {
                            "from_stop_id": from_stop_id,
                            "to_stop_id": to_stop_id,
                            "transfer_type": "2",
                            "min_transfer_time": min_transfer_time,
                        }
                    )
    return rows
