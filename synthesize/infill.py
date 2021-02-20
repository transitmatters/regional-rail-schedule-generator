from synthesize.util import get_pairs


def infill(station_names, *station_triples):
    next_station_names = list(station_names)
    for match_first, new_station, match_second in station_triples:
        for index, (first, second) in enumerate(get_pairs(next_station_names)):
            if first == match_first and second == match_second:
                next_station_names = (
                    next_station_names[0 : index + 1]
                    + [new_station]
                    + next_station_names[index + 1 :]
                )
                break
        else:
            raise Exception(
                f"Unable to add station {new_station} between {match_first} and {match_second}"
            )
    return tuple(next_station_names)
