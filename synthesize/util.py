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


def map_interim_to_non_interim(stop_id: str, stop_name: str = None):
    """
    If the stop_id or stop_name refers to an interim stop, return the non-interim version.
    Otherwise, return the original values.
    """
    # Example mapping for Lynn Interim
    interim_to_non_interim = {
        # parent station
        "place-ER-0117": "place-ER-0115",
        # child stops
        "ER-0117-01": "ER-0115-01",
        "ER-0117-02": "ER-0115-02",
    }
    # If more interim stops exist, add them here

    # Map by stop_id
    new_id = interim_to_non_interim.get(stop_id, stop_id)

    # Map by stop_name if provided
    if stop_name and "Interim" in stop_name:
        new_name = stop_name.replace("Interim", "").strip()
        if new_name == "":
            new_name = "Lynn"  # fallback for known case
        return new_id, new_name
    return new_id
