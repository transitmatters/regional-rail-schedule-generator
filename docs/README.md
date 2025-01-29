# Regional Rail Schedule Generator

Generate a new GTFS schedule bundle for a proposed new MBTA service

## How to use

TODO

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

TODO

### How to add a new Scenario

TODO

## Dev Setup

Dev setup is fairly simple.

- Python 3.12 with recent poetry (2.0.0 or later)
  - Verify with `python --version && poetry --version`
  - `poetry self update` to update poetry
  - Then run `poetry install` to download dependencies

After that all commands you need will be found in the `Makefile`
