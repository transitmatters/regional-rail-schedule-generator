install-git-hooks:
	rm -f ./.git/hooks/* && cp ./.githooks/* ./.git/hooks && chmod +x ./.git/hooks/*

format:
	black .

lint:
	flake8 && black --check .

select-gtfs:
	poetry run python -m network.mbta_gtfs --date=$(date)

existing-network:
	rm -f data/network.pickle
	poetry run python -m network.relevant_stop_times
	poetry run python -m network.main

regional-rail:
	poetry run python -m scenarios.regional_rail

build:
	make select-gtfs date=$(date)
	make existing-network
	make regional-rail