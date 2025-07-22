import os
import pickle
import sys

from .build import build_network_from_gtfs
from .config import PATH_TO_PICKLED_NETWORK

LARGE_RECURSION_LIMIT = 10000


def get_gtfs_network():
    print("Creating network from scratch...")
    network = build_network_from_gtfs()
    return network


if __name__ == "__main__":
    get_gtfs_network()
