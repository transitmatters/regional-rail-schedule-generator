from typing import Dict
import datetime


def time_from_string(time_string):
    pieces = [int(x) for x in time_string.split(":")]
    if len(pieces) == 3:
        hours, minutes, seconds = pieces
        return datetime.timedelta(hours=hours, minutes=minutes, seconds=seconds)
    hours, minutes = pieces
    return datetime.timedelta(hours=hours, minutes=minutes)


def time_range_from_string(time_string):
    pieces = time_string.split("-")
    assert len(pieces) == 2
    return tuple(time_from_string(piece.strip()) for piece in pieces)


def stringify_timedelta(td):
    seconds = td.total_seconds()
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    return f"{int(hours)}:{int(minutes)}:{int(seconds)}"


def parse_schedule_dict(dn: Dict[str, float]):
    return {
        service: {
            time_range_from_string(time_range_string): frequency
            for (time_range_string, frequency) in service_dict.items()
        }
        for (service, service_dict) in dn.items()
    }


def parse_travel_time_dict(dn: Dict[str, str]):
    return {
        station_name: time_from_string(time_offset)
        for (station_name, time_offset) in dn.items()
    }


DAYS_OF_WEEK = [
    "monday",
    "tuesday",
    "wednesday",
    "thursday",
    "friday",
    "saturday",
    "sunday",
]
