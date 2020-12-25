from functools import wraps
from types import GeneratorType


def get_triples(some_list):
    for index in range(len(some_list) - 2):
        yield some_list[index], some_list[index + 1], some_list[index + 2]


def get_pairs(some_list):
    for index in range(len(some_list) - 1):
        yield some_list[index], some_list[index + 1]


def listify(func):
    @wraps(func)
    def new_func(*args, **kwargs):
        r = func(*args, **kwargs)
        if isinstance(r, GeneratorType):
            return list(r)
        else:
            return r

    return new_func


def infill(station_names, *station_triples):
    next_station_names = list(station_names)
    for match_first, new_station, match_second in station_triples:
        for index, (first, second) in enumerate(get_pairs(next_station_names)):
            if first == match_first and second == match_second:
                next_station_names = (
                    next_station_names[0 : index + 1]
                    + [new_station if isinstance(new_station, str) else new_station.name]
                    + next_station_names[index + 1 :]
                )
                break
        else:
            raise Exception(
                f"Unable to add station {new_station} between {match_first} and {match_second}"
            )
    return next_station_names
