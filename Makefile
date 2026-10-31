install-git-hooks:
	uv run pre-commit install

format:
	uv run ruff check --fix .
	uv run ruff format .

lint:
	uv run ruff check .
	uv run ruff format --check .

test:
	uv run pytest

select-gtfs:
	uv run python -m network.mbta_gtfs --date=$(date)

update-gtfs:
	uv run python -m network.update_gtfs

existing-network:
	rm -f data/network.pickle
	uv run python -m network.relevant_stop_times
	uv run python -m network.main

regional-rail:
	uv run python -m scenarios.regional_rail

generate-timetable:
	uv run python -m generate.generate_timetable $(gtfs_path) $(route_id) $(output_path)

build:
	make select-gtfs date=$(date)
	make update-gtfs
	make existing-network
	make regional-rail
