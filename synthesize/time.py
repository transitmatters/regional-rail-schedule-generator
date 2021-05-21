from typing import Dict

from network.time import time_from_string, time_range_from_string, DAYS_OF_WEEK
from network.models import Service


class Timetable(object):
    def __init__(self, str_times_dict: Dict[any, str] = None):
        if str_times_dict:
            self.travel_times = {
                station_name: time_from_string(time_offset)
                for (station_name, time_offset) in str_times_dict.items()
            }
        else:
            self.travel_times = {}

    def contains(self, key):
        return key in self.travel_times

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
            map_keys(key): map_values(value)
            for (key, value) in self.travel_times.items()
        }
        return new


Weekdays = Service(
    id="weekdays",
    days=DAYS_OF_WEEK[0:5],
    description="Weekdays",
    schedule_name="Weekdays",
    schedule_type="Weekday",
    schedule_typicality=4,
)

Saturday = Service(
    id="saturday",
    days=["saturday"],
    description="Saturday",
    schedule_name="Saturday",
    schedule_type="Saturday",
    schedule_typicality=4,
)

Sunday = Service(
    id="sunday",
    days=["sunday"],
    description="Sunday",
    schedule_name="Sunday",
    schedule_type="Sunday",
    schedule_typicality=4,
)


def all_day_frequencies(headway):
    day_schedule = {
        time_range_from_string("05:00-23:59"): headway,
    }
    return {
        Weekdays: day_schedule,
        Saturday: day_schedule,
        Sunday: day_schedule,
    }


def peak_offpeak_frequencies(peak_headway, off_peak_headway):
    day_schedule = {
        time_range_from_string("05:00-06:30"): off_peak_headway,
        time_range_from_string("06:30-11:00"): peak_headway,
        time_range_from_string("11:00-16:30"): off_peak_headway,
        time_range_from_string("16:30-19:00"): peak_headway,
        time_range_from_string("19:00-23:59"): off_peak_headway,
    }
    return {
        Weekdays: day_schedule,
        Saturday: day_schedule,
        Sunday: day_schedule,
    }


all_day_15 = all_day_frequencies(15)
all_day_30 = all_day_frequencies(30)
