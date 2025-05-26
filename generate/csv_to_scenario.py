import argparse
import csv
from typing import Dict, List, Tuple

def parse_csv_time_to_int_minutes(csv_time_str: str) -> int:
    """Converts CSV time string to total integer minutes. Truncates seconds.
    Expected formats: "H:MM:SS", "M:SS", "M" (as string), or "-"."""
    clean_str = csv_time_str.strip()
    if not clean_str or clean_str == '-':
        return 0

    parts = clean_str.split(':')
    try:
        if len(parts) == 1:  # M (total minutes)
            return int(parts[0])
        elif len(parts) == 2:  # M:SS (treat parts[0] as minutes)
            return int(parts[0])
        elif len(parts) == 3:  # H:MM:SS
            return int(parts[0]) * 60 + int(parts[1])
        else:
            raise ValueError("Time string has too many parts.")
    except ValueError as e:
        raise ValueError(f"Invalid time component in '{clean_str}': {e}")

def format_int_minutes_to_timetable_str(total_minutes: int) -> str:
    """Converts total integer minutes to "H:MM" string format."""
    if total_minutes < 0:
        # This should ideally be prevented by adjustment logic ensuring non-negative times.
        print(f"Warning: Negative total_minutes ({total_minutes}) received. Defaulting to \"0:00\".")
        total_minutes = 0
    hours = total_minutes // 60
    minutes = total_minutes % 60
    return f"{hours}:{str(minutes).zfill(2)}"

def generate_scenario_content(
    route_variable_name: str,
    route_id: str,
    route_name: str,
    pattern_id: str,
    pattern_name: str,
    stations: List[str],
    timetable_dict: Dict[str, str], # Expects "H:MM" format
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
    parser.add_argument("--csv-station-col", type=int, default=1, help="0-indexed column for station names in CSV (default: 1 to match common CSV structure after headers).")
    parser.add_argument("--csv-time-col", type=int, default=5, help="0-indexed column for cumulative travel times in CSV (H:MM:SS, M:SS, or M).")

    args = parser.parse_args()

    stations_data: List[Tuple[str, str]] = [] 

    with open(args.input_csv, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        for _ in range(args.csv_skip_rows):
            try:
                next(reader) 
            except StopIteration:
                print(f"Warning: CSV file has fewer than {args.csv_skip_rows} rows to skip.")
                break
        
        for row_idx, row in enumerate(reader):
            if not any(field.strip() for field in row): 
                continue
            if len(row) > max(args.csv_station_col, args.csv_time_col):
                station_name = row[args.csv_station_col].strip()
                cumulative_time_str = row[args.csv_time_col].strip() 
                if station_name:
                    stations_data.append((station_name, cumulative_time_str))
                elif cumulative_time_str:
                    print(f"Warning: Row {row_idx + args.csv_skip_rows + 1}: Station name is empty but time ('{cumulative_time_str}') is present. Skipping row.")
            else:
                print(f"Skipping row {row_idx + args.csv_skip_rows + 1} due to insufficient columns: {row}")

    if not stations_data:
        print("No station data found or parsed from CSV. Exiting.")
        return

    # Process stations to ensure unique, increasing integer minute times internally
    # then convert to "H:MM" strings for the timetable_dict
    processed_timetable_dict: Dict[str, str] = {}
    processed_station_names: List[str] = []
    last_processed_int_minutes = -1

    for station_idx, (station_name, raw_csv_time_str) in enumerate(stations_data):
        current_csv_int_minutes: int
        try:
            # Handles empty, '-', H:MM:SS, M:SS, M
            current_csv_int_minutes = parse_csv_time_to_int_minutes(raw_csv_time_str)
        except ValueError as e:
            print(f"Error parsing time '{raw_csv_time_str}' for station '{station_name}': {e}. Skipping station.")
            continue # Skip this station

        adjusted_int_minutes = current_csv_int_minutes
        if station_idx == 0: # First station
            if adjusted_int_minutes < 0: # Ensure first station time is at least 0
                print(f"Info: First station '{station_name}' CSV time parsed to {adjusted_int_minutes} min. Adjusting to 0 min.")
                adjusted_int_minutes = 0
        elif adjusted_int_minutes <= last_processed_int_minutes: 
            original_time_for_log = adjusted_int_minutes
            adjusted_int_minutes = last_processed_int_minutes + 1
            print(f"Info: Adjusting time for station '{station_name}'. Original parsed: {original_time_for_log} min, previous adjusted: {last_processed_int_minutes} min. New time: {adjusted_int_minutes} min.")
        
        # Add to processed lists
        processed_station_names.append(station_name)
        processed_timetable_dict[station_name] = format_int_minutes_to_timetable_str(adjusted_int_minutes)
        last_processed_int_minutes = adjusted_int_minutes

    if not processed_timetable_dict:
        print("No valid station times could be processed to create a timetable. Exiting.")
        return

    py_content = generate_scenario_content(
        route_variable_name=args.route_variable_name,
        route_id=args.route_id,
        route_name=args.route_name,
        pattern_id=args.pattern_id,
        pattern_name=args.pattern_name,
        stations=processed_station_names,
        timetable_dict=processed_timetable_dict,
        peak_headway=args.peak_headway,
        offpeak_headway=args.offpeak_headway,
        shadows_real_route=args.shadows_real_route,
    )

    with open(args.output_py, 'w', encoding='utf-8') as f:
        f.write(py_content)

    print(f"Successfully generated {args.output_py} from {args.input_csv}")

if __name__ == "__main__":
    main()
