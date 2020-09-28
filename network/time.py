import datetime


def time_from_string(time_string):
    hours, minutes, seconds = [int(x) for x in time_string.split(":")]
    return datetime.timedelta(hours=hours, minutes=minutes, seconds=seconds)


def stringify_timedelta(td):
    seconds = td.total_seconds()
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    return f"{int(hours)}:{int(minutes)}:{int(seconds)}"


DAYS_OF_WEEK = [
    "monday",
    "tuesday",
    "wednesday",
    "thursday",
    "friday",
    "saturday",
    "sunday",
]
