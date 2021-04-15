install-git-hooks:
	rm -f ./.git/hooks/* && cp ./.githooks/* ./.git/hooks && chmod +x ./.git/hooks/*

format:
	black .

lint:
	flake8 && black --check .

existing-network:
	rm -f data/network.pickle
	python3 -m network.relevant_stop_times
	python3 -m network.main

phase-one:
	python3 -m scenarios.phase_one