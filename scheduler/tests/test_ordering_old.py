from scheduler.ordering_old import get_plausible_service_orderings
from scheduler.network import create_scheduler_network
from scheduler.service_pattern_graph import ServicePatternGraph
from scheduler.tests.data import route_patterns


def test_ordering_with_tph():
    orderings = get_plausible_service_orderings(trips_per_period={"a": 2, "b": 2})
    assert orderings == {("a", "b", "a", "b"), ("b", "a", "b", "a")}


def test_ordering_with_service_pattern_graph():
    network = create_scheduler_network(route_patterns)
    spg = ServicePatternGraph.from_scheduler_network(network)
    orderings = get_plausible_service_orderings(
        trips_per_period={"x": 2, "y": 2, "z": 3},
        service_pattern_graph=spg,
        strict_order_checking=True,
    )
    assert orderings == {
        ("z", "y", "x", "z", "y", "z", "x"),
        ("z", "y", "z", "x", "y", "z", "x"),
        ("z", "y", "x", "z", "y", "x", "z"),
        ("z", "y", "x", "z", "z", "y", "x"),
        ("z", "y", "z", "x", "z", "y", "x"),
    }
