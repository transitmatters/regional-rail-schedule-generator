from scheduler.network import create_scheduler_network
from scheduler.tests.data import route_patterns
from scheduler.scheduling_problem import SchedulingProblem
from scheduler.ordering import get_orderings, Range, proposed_dispatch_is_too_late


def test_ordering():
    network = create_scheduler_network(route_patterns)
    problem = SchedulingProblem(
        trips_per_period={"x": 2, "y": 2, "z": 2},
        network=network,
    )
    orderings = get_orderings(problem)
    assert len(orderings) == 10


def test_range_intersection():
    range1 = Range(0, 10)
    range2 = Range(5, 15)
    intersection = range1.intersection(range2)
    assert intersection.lower == 5
    assert intersection.upper == 10

    range3 = Range(10, 20)
    intersection = range1.intersection(range3)
    assert intersection is None


def test_range_offset():
    range1 = Range(0, 10)
    offset_range = range1.offset(5)
    assert offset_range.lower == 5
    assert offset_range.upper == 15


def test_proposed_dispatch_is_too_late():
    network = create_scheduler_network(route_patterns)
    problem = SchedulingProblem(
        trips_per_period={"x": 2, "y": 2, "z": 2},
        network=network,
    )
    sequence = ["x", "y", "z"]
    assert not proposed_dispatch_is_too_late(sequence, "x", problem)
    assert not proposed_dispatch_is_too_late(sequence, "y", problem)
    assert not proposed_dispatch_is_too_late(sequence, "z", problem)
