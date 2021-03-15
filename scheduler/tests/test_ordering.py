from scheduler.ordering import get_orderings
from scheduler.network import create_scheduler_network
from scheduler.tests.data import route_patterns
from scheduler.scheduling_problem import SchedulingProblem


def test_ordering():
    network = create_scheduler_network(route_patterns)
    problem = SchedulingProblem(
        trips_per_period={"x": 2, "y": 2, "z": 2},
        network=network,
    )
    orderings = get_orderings(problem)
    assert len(orderings) == 10
