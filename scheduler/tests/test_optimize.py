from scheduler.network import create_scheduler_network
from scheduler.tests.data import route_patterns
from scheduler.scheduling_problem import SchedulingProblem
from scheduler.optimize import solve_departure_offsets


def _get_arrivals_at_node(problem, offsets, node_id):
    """Compute sorted arrival times at a node for all visits."""
    arrivals = []
    for service_id, service in problem.services.items():
        node = problem.nodes[node_id]
        if node not in service.calls_at_nodes:
            continue
        headway = problem.get_service_headway(service_id)
        trip_time = service.trip_time_to_node_seconds(node)
        tph = problem.trips_per_period[service_id]
        for k in range(tph):
            arrivals.append(offsets[service_id] + headway * k + trip_time)
    return sorted(arrivals)


def _get_consecutive_gaps(arrivals, period):
    """Return all consecutive gaps including the wrap-around."""
    gaps = [arrivals[i + 1] - arrivals[i] for i in range(len(arrivals) - 1)]
    gaps.append(arrivals[0] + period - arrivals[-1])
    return gaps


def test_solve_departure_offsets():
    network = create_scheduler_network(route_patterns)
    problem = SchedulingProblem(
        trips_per_period={"x": 2, "y": 2, "z": 2},
        network=network,
    )
    offsets = solve_departure_offsets(problem, debug=False)

    assert set(offsets.keys()) == {"x", "y", "z"}
    for sid in offsets:
        headway = problem.get_service_headway(sid)
        assert 0 <= offsets[sid] <= headway

    for node_id in problem.nodes:
        arrivals = _get_arrivals_at_node(problem, offsets, node_id)
        if len(arrivals) < 2:
            continue
        gaps = _get_consecutive_gaps(arrivals, problem.period)
        for gap in gaps:
            assert gap >= problem.exclusion_time, (
                f"Gap {gap}s < exclusion {problem.exclusion_time}s at node {node_id}"
            )


def test_single_service():
    network = create_scheduler_network(route_patterns)
    problem = SchedulingProblem(
        trips_per_period={"x": 4},
        network=network,
    )
    offsets = solve_departure_offsets(problem, debug=False)
    assert "x" in offsets


def test_two_services_even_spacing():
    """Two services at 2 tph sharing a node should achieve ~15-min spacing (4 trains/hr at junction)."""
    network = create_scheduler_network(route_patterns)
    problem = SchedulingProblem(
        trips_per_period={"x": 2, "y": 2},
        network=network,
    )
    offsets = solve_departure_offsets(problem, debug=False)

    for node_id in problem.nodes:
        arrivals = _get_arrivals_at_node(problem, offsets, node_id)
        if len(arrivals) < 2:
            continue
        gaps = _get_consecutive_gaps(arrivals, problem.period)
        ideal_gap = problem.period // len(arrivals)
        for gap in gaps:
            assert gap >= ideal_gap * 0.5, (
                f"Gap {gap}s much smaller than ideal {ideal_gap}s at node {node_id}"
            )
