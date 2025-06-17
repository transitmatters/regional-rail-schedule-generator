import os
import pandas as pd
from datetime import datetime
import argparse


def generate_timetable(gtfs_path: str, route_ids: list, output_path: str):
    # Load GTFS files
    trips = pd.read_csv(os.path.join(gtfs_path, "trips.txt"), low_memory=False)
    stop_times = pd.read_csv(os.path.join(gtfs_path, "stop_times.txt"), low_memory=False)
    stops = pd.read_csv(os.path.join(gtfs_path, "stops.txt"), low_memory=False)

    output_lines = []

    for route_id in route_ids:
        route_trips = trips[trips["route_id"] == route_id]
        if route_trips.empty:
            print(f"[Warning] No trips found for route_id '{route_id}'")
            continue

        # Use the first trip
        sample_trip_id = route_trips.iloc[0]["trip_id"]
        trip_stop_times = stop_times[stop_times["trip_id"] == sample_trip_id].sort_values("stop_sequence")
        merged = trip_stop_times.merge(stops[["stop_id", "stop_name"]], on="stop_id")

        first_time = datetime.strptime(merged.iloc[0]["arrival_time"], "%H:%M:%S")
        merged["offset"] = merged["arrival_time"].apply(lambda t: str(datetime.strptime(t, "%H:%M:%S") - first_time))

        # Clean name for variable (e.g., green_b_timetable)
        var_name = f"{route_id.lower().replace('-', '_')}_timetable"

        timetable_lines = [
            f'    "{row.stop_name}": "{row.offset[:-3] if row.offset.endswith(":00") else row.offset}",'
            for _, row in merged.iterrows()
        ]

        timetable_block = f"{var_name} = Timetable(\n    {{\n" + "\n".join(timetable_lines) + "\n    }\n)\n"
        output_lines.append(timetable_block)

    # Write all blocks to a single file
    with open(output_path, "w") as f:
        f.write("\n".join(output_lines))

    print(f"Branch timetables written to {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a timetable for a specific route")
    parser.add_argument("gtfs_path", help="Path to the GTFS data directory")
    parser.add_argument("route_ids", help="Comma-separated list of route IDs to generate a timetable for")
    parser.add_argument("output_path", help="Path to write the timetable output to")

    args = parser.parse_args()

    # Split the route_ids string by comma
    route_ids_list = [r.strip() for r in args.route_ids.split(",")]

    generate_timetable(args.gtfs_path, route_ids_list, args.output_path)
