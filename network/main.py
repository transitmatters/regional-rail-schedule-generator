import os
import pickle

from .build import load_gtfs_dicts, link_network_from_dicts
from .config import PATH_TO_PICKLED_NETWORK


def get_gtfs_network():
    if os.path.exists(PATH_TO_PICKLED_NETWORK):
        try:
            with open(PATH_TO_PICKLED_NETWORK, "rb") as f:
                gtfs_dicts = pickle.load(f)
            return link_network_from_dicts(gtfs_dicts)
        except Exception:
            print("Error loading cached GTFS data.")

    print("Loading GTFS from CSV...")
    gtfs_dicts = load_gtfs_dicts()
    with open(PATH_TO_PICKLED_NETWORK, "wb") as f:
        pickle.dump(gtfs_dicts, f)
    return link_network_from_dicts(gtfs_dicts)


if __name__ == "__main__":
    get_gtfs_network()
