existing-network:
	rm -f data/network.pickle
	python3 -m network.relevant_stop_times
	python3 -m network.main