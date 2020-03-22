import math
from itertools import zip_longest
from typing import List

from geopy.distance import geodesic
import numpy as np

from network.models import Network, Station, Trip

from .trainset import Trainset
from .util import get_pairs, get_triples

# From Wikipedia (it's the state house, cute)
CENTER_OF_BOSTON = (42.358056, -71.063611)

def debug_geo_shape(geo_shape):
    print("lat, lon")
    for lat, lon in geo_shape:
        print(f"{lat}, {lon}")


# Adapted from here: https://stackoverflow.com/a/50974391
def get_curve_radius_for_points(p1, p2, p3):
    temp = p2[0] * p2[0] + p2[1] * p2[1]
    bc = (p1[0] * p1[0] + p1[1] * p1[1] - temp) / 2
    cd = (temp - p3[0] * p3[0] - p3[1] * p3[1]) / 2
    det = (p1[0] - p2[0]) * (p2[1] - p3[1]) - (p2[0] - p3[0]) * (p1[1] - p2[1])

    cx = (bc * (p2[1] - p3[1]) - cd * (p1[1] - p2[1])) / det
    cy = ((p1[0] - p2[0]) * cd - (p2[0] - p3[0]) * bc) / det
    radius = np.sqrt((cx - p1[0]) ** 2 + (cy - p1[1]) ** 2)
    return radius


def get_degree_of_curvature_for_radius(curve_radius_km):
    return 5729.58 / (curve_radius_km * 3280.84)


def get_max_speed_for_curve_radius_kmh(curve_radius_km):
    return 1.60934 * (
        math.sqrt(6 / (0.0007 * get_degree_of_curvature_for_radius(curve_radius_km)))
    )


def get_point_distance(p1, p2):
    (x1, y1) = p1
    (x2, y2) = p2
    return ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5


def shoddily_convert_point_to_km(point, source=CENTER_OF_BOSTON):
    # These points are in (lat, long) which is like (y, x)
    (y1, x1) = point
    (y2, x2) = source
    x_distance = geodesic((x1, y1), (x2, y1)).km
    y_distance = geodesic((x1, y1), (x1, y2)).km
    x_distance_signed = (1 if x1 > x2 else -1) * x_distance
    y_distance_signed = (1 if y1 > y2 else -1) * y_distance
    return (x_distance_signed, y_distance_signed)


def get_exemplar_trip_for_stations(
    network: Network, first: Station, second: Station
) -> Trip:
    all_trips = network.trips_by_id.values()

    def trip_serves_station(trip: Trip, station: Station):
        return station in (
            stop_time.stop.parent_station for stop_time in trip.stop_times
        )

    try:
        return next(
            trip
            for trip in all_trips
            if trip_serves_station(trip, first) and trip_serves_station(trip, second)
        )
    except StopIteration:
        raise Exception(f"No exemplar trip for {first.name} -> {second.name}")


def get_shape_between_stations(network: Network, first: Station, second: Station):
    trip_shape = get_exemplar_trip_for_stations(network, first, second).shape

    def closest_point_towards(target, boundary):
        closest = float("inf")
        closest_index = None
        target_boundary_distance = get_point_distance(target, boundary)
        for index, point in enumerate(trip_shape):
            point_distance = get_point_distance(point, target)
            if (
                point_distance < closest
                and get_point_distance(boundary, point) <= target_boundary_distance
            ):
                closest = point_distance
                closest_index = index
        if closest_index is None:
            raise Exception("Could not find valid closest point")
        return closest_index

    closest_to_first = closest_point_towards(first.location, second.location)
    closest_to_second = closest_point_towards(second.location, first.location)
    return list(dict.fromkeys(trip_shape[closest_to_first : closest_to_second + 1]))


def get_distances_between_points_km(geo_shape):
    res = []
    for p1, p2 in get_pairs(geo_shape):
        res.append(geodesic(p1, p2).km)
    return res


def get_acceleration_bounding_curve(distances, max_acceleration_kms2):
    velocity_curve_kms = np.zeros(len(distances))
    # Start at a standstill
    for index, distance_km in enumerate(distances):
        current_velocity_kms = velocity_curve_kms[index - 1] if index > 0 else 0
        # Solve the equation 0.5 * t * Amax ^ 2 + V * t - D = 0
        time_s = (
            -1 * current_velocity_kms
            + math.sqrt(
                current_velocity_kms ** 2 + 2 * max_acceleration_kms2 * distance_km
            )
        ) / max_acceleration_kms2
        next_velocity_kms = current_velocity_kms + max_acceleration_kms2 * time_s
        velocity_curve_kms[index] = next_velocity_kms
    # Convert back to km/h which is what we use everywhere else
    return list(map(lambda a: 3600 * a, velocity_curve_kms))


def get_track_geometry_bounding_curve(shape):
    shape_km = list(map(shoddily_convert_point_to_km, shape))
    res = []
    for (k1, k2, k3) in get_triples(shape_km):
        curve_radius = get_curve_radius_for_points(k1, k2, k3)
        max_speed_kmh = get_max_speed_for_curve_radius_kmh(curve_radius)
        res.append(max_speed_kmh)
    return [res[0]] + res


def estimate_travel_time_between_stations_seconds(
    network: Network, first: Station, second: Station, trainset: Trainset
):
    assert first in network.stations_by_id.values()
    assert second in network.stations_by_id.values()
    geo_shape = get_shape_between_stations(network, first, second)
    distances_km = get_distances_between_points_km(geo_shape)
    acceleration_curve_kmh = get_acceleration_bounding_curve(
        distances_km, trainset.max_acceleration_kms2
    )
    decceleration_curve_kmh = list(
        reversed(
            get_acceleration_bounding_curve(
                list(reversed(distances_km)), trainset.max_decceleration_kms2
            )
        )
    )
    track_geometry_bounding_curve_kmh = get_track_geometry_bounding_curve(geo_shape)
    total_time_h = 0
    total_distance_km = 0
    for index, distance_km in enumerate(distances_km):
        plausible_speed_kmh = min(
            trainset.max_velocity_kms,
            track_geometry_bounding_curve_kmh[index],
            acceleration_curve_kmh[index],
            decceleration_curve_kmh[index],
        )
        total_time_h += distance_km / plausible_speed_kmh
        total_distance_km += distance_km
    return 3600 * total_time_h
