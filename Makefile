install-git-hooks:
	rm -f ./.git/hooks/* && cp ./.githooks/* ./.git/hooks && chmod +x ./.git/hooks/*

format:
	black .

lint:
	flake8 && black --check .

select-gtfs:
	poetry run python -m network.mbta_gtfs --date=$(date)

update-gtfs:
	poetry run python -m network.update_gtfs

existing-network:
	rm -f data/network.pickle
	poetry run python -m network.relevant_stop_times
	poetry run python -m network.main

regional-rail:
	poetry run python -m scenarios.regional_rail

expansion:
	poetry run python -m scenarios.expansion

generate-timetable:
	poetry run python -m generate.generate_timetable $(gtfs_path) $(route_id) $(output_path)

build:
	make select-gtfs date=$(date)
	make update-gtfs
	make existing-network
	make regional-rail
	make expansion