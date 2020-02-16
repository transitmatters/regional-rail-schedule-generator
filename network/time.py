import datetime


def time_from_string(time_string):
    hours, minutes, seconds = [int(x) for x in time_string.split(":")]
    return datetime.timedelta(hours=hours, minutes=minutes, seconds=seconds)


DAYS_OF_WEEK = [
    "monday",
    "tuesday",
    "wednesday",
    "thursday",
    "friday",
    "saturday",
    "sunday",
]
