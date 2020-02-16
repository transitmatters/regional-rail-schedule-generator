import os
import pickle
import sys

from .build import build_network_from_gtfs
from .config import PATH_TO_PICKLED_NETWORK

LARGE_RECURSION_LIMIT = 10000


def get_gtfs_network():
    if os.path.exists(PATH_TO_PICKLED_NETWORK):
        with open(PATH_TO_PICKLED_NETWORK, "rb") as file:
            try:
                return pickle.load(file)
            except Exception:
                print("Error loading pickled network.")
    print("Creating network from scratch...")
    network = build_network_from_gtfs()
    with open(PATH_TO_PICKLED_NETWORK, "wb") as file:
        old_limit = sys.getrecursionlimit()
        sys.setrecursionlimit(LARGE_RECURSION_LIMIT)
        pickle.dump(network, file)
        sys.setrecursionlimit(old_limit)
        return network


if __name__ == "__main__":
    get_gtfs_network()
