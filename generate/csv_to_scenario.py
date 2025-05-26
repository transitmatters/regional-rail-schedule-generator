import argparse
import csv
from typing import Dict, List, Tuple

def parse_time_to_str(time_str: str) -> str:
    """Converts H:MM:SS or M:SS to 0:MM string format for Timetable."""
    parts = time_str.split(':')
    if len(parts) == 3: # H:MM:SS
        return f"0:{parts[1].zfill(2)}"
    elif len(parts) == 2: # M:SS
        return f"0:{parts[0].zfill(2)}"
    elif len(parts) == 1 and parts[0] == '-': # Handle empty time for the first station
        return "0:00"
    raise ValueError(f"Unexpected time format: {time_str}")

def generate_scenario_content(
    route_variable_name: str,
    route_id: str,
    route_name: str,
    pattern_id: str,
    pattern_name: str,
    stations: List[str],
    timetable_dict: Dict[str, str],
    peak_headway: int,
    offpeak_headway: int,
    shadows_real_route: str = None,
) -> str:
    """Generates the Python code for the scenario file."""
    station_list_str = ",\n    ".join([f'"{s}"' for s in stations])
    timetable_items_str = ",\n        ".join([f'"{k}": "{v}"' for k, v in timetable_dict.items()])

    shadow_line = ""
    if shadows_real_route:
        shadow_line = f'shadows_real_route="{shadows_real_route}",'

    content = f"""from synthesize.definitions import Route, RoutePattern
from synthesize.time import Timetable, peak_offpeak_frequencies

timetable = Timetable(
    {{
        {timetable_items_str}
    }}
)

stations = (
    {station_list_str},
)

{route_variable_name} = Route(
    id="{route_id}",
    {shadow_line}
    name="{route_name}",
    route_patterns=[
        RoutePattern(
            id="{pattern_id}",
            name="{pattern_name}",
            stations=stations,
            timetable=timetable,
            schedule=peak_offpeak_frequencies({peak_headway}, {offpeak_headway}),
        )
    ],
)
"""
    return content

def main():
    parser = argparse.ArgumentParser(description="Generate a scenario Python file from a CSV.")
    parser.add_argument("--input-csv", required=True, help="Path to the input CSV file.")
    parser.add_argument("--output-py", required=True, help="Path for the generated Python scenario file.")
    parser.add_argument("--route-variable-name", required=True, help="Python variable name for the Route object (e.g., blue).")
    parser.add_argument("--route-id", required=True, help="ID for the Route object (e.g., 'Blue').")
    parser.add_argument("--route-name", required=True, help="Descriptive name for the Route (e.g., 'Blue Line').")
    parser.add_argument("--pattern-id", required=True, help="ID for the RoutePattern object (e.g., 'blue-pattern').")
    parser.add_argument("--pattern-name", required=True, help="Descriptive name for the RoutePattern (e.g., 'Blue Line Main Pattern').")
    parser.add_argument("--shadows-real-route", help="Optional ID of a real route this scenario shadows.")
    parser.add_argument("--peak-headway", type=int, default=5, help="Peak headway in minutes.")
    parser.add_argument("--offpeak-headway", type=int, default=7, help="Off-peak headway in minutes.")
    parser.add_argument("--csv-skip-rows", type=int, default=8, help="Number of header rows to skip in the CSV.")
    parser.add_argument("--csv-station-col", type=int, default=1, help="0-indexed column for station names in CSV.")
    parser.add_argument("--csv-time-col", type=int, default=5, help="0-indexed column for cumulative travel times in CSV (H:MM:SS or M:SS).")


    args = parser.parse_args()

    stations_data: List[Tuple[str, str]] = [] # List of (station_name, cumulative_time_str)

    with open(args.input_csv, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        for _ in range(args.csv_skip_rows):
            next(reader)  # Skip header rows
        
        for row in reader:
            if not any(field.strip() for field in row): # Skip entirely empty rows
                continue
            if len(row) > max(args.csv_station_col, args.csv_time_col):
                station_name = row[args.csv_station_col].strip()
                cumulative_time_str = row[args.csv_time_col].strip()
                if station_name: # Ensure station name is not empty
                    stations_data.append((station_name, cumulative_time_str))
            else:
                print(f"Skipping row due to insufficient columns: {row}")


    if not stations_data:
        print("No station data found in CSV. Exiting.")
        return

    station_names: List[str] = [sd[0] for sd in stations_data]
    timetable_dict: Dict[str, str] = {}

    # The first station's time is the baseline (0:00)
    # For subsequent stations, the CSV provides cumulative time.
    # The Timetable expects offsets from the *first* station.
    first_station_name = stations_data[0][0]
    timetable_dict[first_station_name] = "0:00"

    for i in range(len(stations_data)):
        current_station_name = stations_data[i][0]
        # The time in CSV is cumulative from the *start* of the line.
        # Timetable wants time from the *first station listed in the timetable argument*.
        # For this script, we assume the first station in the CSV is the start of the timetable.
        cumulative_time_value_str = stations_data[i][1]
        
        # Handle cases like "-" for the first station or empty strings
        if not cumulative_time_value_str or cumulative_time_value_str == '-':
            if i == 0: # First station, time is 0:00
                 timetable_dict[current_station_name] = "0:00"
            else: # Should not happen for subsequent stations if CSV is well-formed
                print(f"Warning: Empty or '-' time for non-first station '{current_station_name}'. Using previous time or 0:00 if first.")
                # Attempt to use previous station's time or default to 0:00
                # This might not be correct if times are truly missing.
                if i > 0 and stations_data[i-1][0] in timetable_dict:
                    timetable_dict[current_station_name] = timetable_dict[stations_data[i-1][0]]
                else:
                    timetable_dict[current_station_name] = "0:00"
        else:
            timetable_dict[current_station_name] = parse_time_to_str(cumulative_time_value_str)


    py_content = generate_scenario_content(
        route_variable_name=args.route_variable_name,
        route_id=args.route_id,
        route_name=args.route_name,
        pattern_id=args.pattern_id,
        pattern_name=args.pattern_name,
        stations=station_names,
        timetable_dict=timetable_dict,
        peak_headway=args.peak_headway,
        offpeak_headway=args.offpeak_headway,
        shadows_real_route=args.shadows_real_route,
    )

    with open(args.output_py, 'w', encoding='utf-8') as f:
        f.write(py_content)

    print(f"Successfully generated {args.output_py} from {args.input_csv}")

if __name__ == "__main__":
    main()
