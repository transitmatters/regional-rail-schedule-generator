import csv
import os
from pathlib import Path

from .config import PATH_TO_GTFS_DATA
from synthesize.util import map_interim_to_non_interim


def update_stops_file(file_path: str) -> None:
    """Update stops.txt to use non-interim stop IDs and remove any rows with stop_name containing 'Interim'."""

    # Read all stops
    stops = []
    with open(file_path, "r") as f:
        reader = csv.reader(f)
        header = next(reader)
        for row in reader:
            if len(row) >= 2:
                stop_name = row[1]
                # Skip rows where stop_name contains 'Interim'
                if "Interim" in stop_name:
                    continue
                stops.append(row)

    # Write updated stops back to file
    with open(file_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(stops)

    print(f"Updated stops file: {file_path}")


def update_stop_times_file(file_path: str) -> None:
    """Update stop_times.txt to use non-interim stop IDs and remove shuttle trips."""
    # Read all stop times
    stop_times = []
    with open(file_path, "r") as f:
        reader = csv.reader(f)
        header = next(reader)
        trip_id_index = header.index("trip_id")
        for row in reader:
            if len(row) >= trip_id_index + 1:
                # Skip shuttle trips
                if row[trip_id_index].startswith("Shuttle-"):
                    continue
                stop_id_index = header.index("stop_id")
                mapped_id = map_interim_to_non_interim(row[stop_id_index])
                if mapped_id != row[stop_id_index]:
                    row[stop_id_index] = mapped_id
                stop_times.append(row)

    # Write updated stop times back to file
    with open(file_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(stop_times)

    print(f"Updated stop times file: {file_path}")


def update_transfers_file(file_path: str) -> None:
    """Update transfers.txt to use non-interim stop IDs."""
    if not os.path.exists(file_path):
        return

    # Read all transfers
    transfers = []
    with open(file_path, "r") as f:
        reader = csv.reader(f)
        header = next(reader)
        for row in reader:
            if len(row) >= 2:  # Ensure row has enough fields
                from_stop_id_index = header.index("from_stop_id")
                to_stop_id_index = header.index("to_stop_id")
                # Map from_stop_id
                mapped_from = map_interim_to_non_interim(row[from_stop_id_index])
                if mapped_from != row[from_stop_id_index]:
                    row[from_stop_id_index] = mapped_from
                # Map to_stop_id
                mapped_to = map_interim_to_non_interim(row[to_stop_id_index])
                if mapped_to != row[to_stop_id_index]:
                    row[to_stop_id_index] = mapped_to
                transfers.append(row)

    # Write back the updated transfers
    with open(file_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(transfers)

    print(f"Updated transfers file: {file_path}")


def update_trips_file(file_path: str) -> None:
    """Update trips.txt to remove any rows with route_id containing 'Shuttle-'."""
    # Read all trips
    trips = []
    with open(file_path, "r") as f:
        reader = csv.reader(f)
        header = next(reader)
        route_id_index = header.index("route_id")
        for row in reader:
            if len(row) >= route_id_index + 1:
                route_id = row[route_id_index]
                # Skip rows where route_id contains 'Shuttle-'
                if route_id.startswith("Shuttle-"):
                    continue
                trips.append(row)

    # Write updated trips back to file
    with open(file_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(trips)

    print(f"Updated trips file: {file_path}")


def update_gtfs_files():
    """Update all relevant GTFS files to map interim stops to non-interim versions."""
    print("Updating GTFS files...")
    gtfs_dir = Path(PATH_TO_GTFS_DATA)

    # Update stops.txt
    stops_file = gtfs_dir / "stops.txt"
    if stops_file.exists():
        print("Updating stops.txt...")
        update_stops_file(str(stops_file))

    # Update stop_times.txt
    stop_times_file = gtfs_dir / "stop_times.txt"
    if stop_times_file.exists():
        print("Updating stop_times.txt...")
        update_stop_times_file(str(stop_times_file))

    # Update trips.txt
    trips_file = gtfs_dir / "trips.txt"
    if trips_file.exists():
        print("Updating trips.txt...")
        update_trips_file(str(trips_file))

    # Update transfers.txt if it exists
    transfers_file = gtfs_dir / "transfers.txt"
    if transfers_file.exists():
        print("Updating transfers.txt...")
        update_transfers_file(str(transfers_file))

    print("GTFS files updated successfully.")


if __name__ == "__main__":
    update_gtfs_files()
