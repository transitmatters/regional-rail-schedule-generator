from scheduler.network import create_scheduler_network
from scheduler.variables import Variables
from scheduler.optimize import (
    get_objective_function,
    solve_departure_offsets,
)
from scheduler.tests.data import route_patterns, trains_per_hour

network = create_scheduler_network(route_patterns, trains_per_hour)


def test_solve_departure_offsets_for_services():
    offsets = solve_departure_offsets(network)
    assert round(offsets["x"]) == 300
    assert round(offsets["y"]) == 731
    assert round(offsets["z"]) == 22
