# Regional Rail Schedule Generator

Generate a new GTFS schedule bundle for a proposed new MBTA service

### How to update GTFS Bundles

To update the GTFS bundles, you need to pull down a bundle for a specific date, and then re-run the scenario generation.

```bash
make build date=YYYY-MM-DD
```
This will update all files under `data/` for GTFS both present and for each scenario

### How to add new stop

In order to add a completely new stop, you'll need to define an Infill Station.

In each scenario, there should be an `infill_stations.py` file. This file will be where you define new stops that don't currently exist in the network. 

#### Using InfillStation (Recommended)

The easiest way to create new infill stations is using the `InfillStation` class, which automatically generates consistent IDs based on the route type:

```python
from synthesize.definitions import InfillStation

# Regional Rail station (default route type)
station_revere_center = InfillStation(
    name="Revere Center",
    id="",  # Auto-generated: place-rr-revere-center
    location=(42.4154533, -70.9922548),
    municipality="Revere",
    route_type="regional_rail"  # Optional, this is the default
)

# Green Line Extension station
station_needham_heights = InfillStation(
    name="Needham Heights",
    id="",  # Auto-generated: place-glx-union-square-west
    location=(42.2936, -71.2364),
    municipality="Needham",
    route_type="green_line_extension"
)

# Blue Line Extension station
station_lynn_central = InfillStation(
    name="Lynn Central",
    id="",  # Auto-generated: place-blx-lynn-central
    location=(42.4668, -70.9495),
    municipality="Lynn",
    route_type="blue_line_extension"
)

# Red Line Extension station
station_arlington = InfillStation(
    name="Arlington Heights",
    id="",  # Auto-generated: place-rlx-arlington-heights
    location=(42.4154, -71.1564),
    municipality="Arlington",
    route_type="red_line_extension"
)
```

**Supported route types:**
- `regional_rail`: Regional Rail (generates `place-rr-` prefix) - default
- `green_line_extension`: Green Line Extension (generates `place-glx-` prefix)
- `blue_line_extension`: Blue Line extensions (generates `place-blx-` prefix)
- `orange_line_extension`: Orange Line extensions (generates `place-olx-` prefix)
- `red_line_extension`: Red Line extensions (generates `place-rlx-` prefix)
- `silver_line_extension`: Silver Line extensions (generates `place-slx-` prefix)

#### Using Station (Legacy)

You can still manually create stations if you need custom IDs:

```python
from synthesize.definitions import Station

station_revere_center = Station(
    name="Revere Center",
    id="place-rr-revere-center",  # Manually specified
    location=(42.4154533, -70.9922548),
    municipality="Revere",
)
```

If you simply want to add a stop that already exists to a new route, you don't need to define a new infill station. You simply need to just add the stop to your scenario's schedule.

### How to add new Route

To add a new route, you'll need a few definitions.

First a timetable, this defines how long it takes to get from stop to stop on the line
```python
timetable = Timetable(
    {
        "Lynn": "0:00",
        "River Works": "0:02",
        ...
    }
)
```

Then a list of all stations in the line
```python
stations = (
    "Lynn",
    "River Works",
    ...
)
```

Then define a new `Route`. Here's an example with the Blue line.

```python
blue = Route(
    id="Blue",
    shadows_real_route="Blue",
    name="Blue Line",
    route_patterns=[
        RoutePattern(
            id="blue",
            name="Blue",
            stations=stations,
            timetable=timetable,
            schedule=all_day_5,
        )
    ],
)
```

If you are making a Route that doesn't currently exist in the system, you can exclude the `shadows_real_route` and it'll default to `None`.

Then in the scenario you are adding the line to, import your new route and add it in the subgraphs where it belongs

```python
subgraphs = [
    [red],
    [blue],
    ...
]
```

### How to add a new Scenario

A new scenario needs only a few elements. You can copy a lot of how the `regional_rail` scenario is defined.

You need a list of lines, infill stations (if your scenario needs any), and a file to write scenarios out to GTFS from the subgraphs.

```python
scenario = evaluate_scenario(subgraphs)
write_scenario_gtfs(scenario, "gtfs-regional-rail")
archive_scenario_gtfs("gtfs-present")
archive_scenario_gtfs("gtfs-regional-rail")
```

## Dev Setup

Dev setup is fairly simple.

- Python 3.12 with recent poetry (2.0.0 or later)
  - Verify with `python --version && poetry --version`
  - `poetry self update` to update poetry
  - Then run `poetry install` to download dependencies

After that all commands you need will be found in the `Makefile`
