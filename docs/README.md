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

In each scenario, there should be an `infill_stations.py` file. This file will be where you define new stops that don't currently exist in the network. An example:

```python
station_revere_center = Station(
    name="Revere Center",
    id="place-rr-revere-center",
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
