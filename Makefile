install-git-hooks:
	rm -f ./.git/hooks/* && cp ./.githooks/* ./.git/hooks && chmod +x ./.git/hooks/*

format:
	black .

lint:
	flake8 && black --check .

select-gtfs:
	python3 -m network.mbta_gtfs --date=$(date)

existing-network:
	rm -f data/network.pickle
	python3 -m network.relevant_stop_times
	python3 -m network.main

regional-rail:
	python3 -m scenarios.regional_rail

build:
	make select-gtfs date=$(date)
	make existing-network
	make regional-rail