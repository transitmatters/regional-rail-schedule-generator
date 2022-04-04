from os.path import dirname, join

PATH_TO_DATA = join(dirname(__file__), "..", "data")
PATH_TO_GTFS_DATA = join(PATH_TO_DATA, "gtfs-present")
PATH_TO_PICKLED_NETWORK = join(PATH_TO_DATA, "network.pickle")
