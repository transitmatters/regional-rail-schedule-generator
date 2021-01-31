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


class Timetable(object):
    def __init__(self, str_times_dict: Dict[any, str] = None):
        if str_times_dict:
            self.travel_times = {
                station_name: time_from_string(time_offset)
                for (station_name, time_offset) in str_times_dict.items()
            }
        else:
            self.travel_times = {}

    def get_travel_time(self, from_key, to_key):
        from_time = self.travel_times.get(from_key)
        to_time = self.travel_times.get(to_key)
        if from_time is not None and to_time is not None:
            return abs(from_time - to_time).seconds
        return None

    def map(self, map_keys=None, map_values=None):
        map_keys = map_keys if map_keys else lambda x: x
        map_values = map_values if map_values else lambda x: x
        new = Timetable()
        new.travel_times = {
            map_keys(key): map_values(value) for (key, value) in self.travel_times.items()
        }
        return new


DAYS_OF_WEEK = [
    "monday",
    "tuesday",
    "wednesday",
    "thursday",
    "friday",
    "saturday",
    "sunday",
]
