from typing import Dict, List, Tuple

import cvxpy as cp

from scheduler.scheduling_problem import SchedulingProblem


def _get_visits_at_nodes(
    problem: SchedulingProblem,
) -> Dict[str, List[Tuple[str, int]]]:
    """For each node with active services, return a list of (service_id, trip_index) visits."""
    visits_at_node = {}
    for node_id, node in problem.nodes.items():
        visits = []
        for service_id, service in problem.services.items():
            if node in service.calls_at_nodes:
                tph = problem.trips_per_period.get(service_id, 0)
                for k in range(tph):
                    visits.append((service_id, k))
        if len(visits) > 1:
            visits_at_node[node_id] = visits
    return visits_at_node


def _count_visit_pairs(visits_at_node: Dict[str, List[Tuple[str, int]]]) -> int:
    """Count total unordered pairs across all nodes (for binary variable allocation)."""
    count = 0
    for visits in visits_at_node.values():
        n = len(visits)
        count += n * (n - 1) // 2
    return count


def _count_wrap_variables(visits_at_node: Dict[str, List[Tuple[str, int]]]) -> int:
    """Count total visits across all nodes (for period-wrap binary allocation)."""
    return sum(len(v) for v in visits_at_node.values())


def solve_departure_offsets(problem: SchedulingProblem, debug=True) -> Dict[str, int]:
    """
    Solve for departure offsets using a single MILP with binary ordering variables,
    replacing the previous enumerate-all-orderings + QP approach.

    At each shared node, binary variables determine the relative ordering of
    train visits (mapped into canonical [0, period) time via wrap variables),
    and big-M constraints enforce minimum exclusion time. The objective maximizes
    the minimum gap between consecutive arrivals at each node.
    """
    services = problem.services
    nodes = problem.nodes
    period = problem.period
    exclusion = problem.exclusion_time
    M = period

    if not services:
        return {}

    visits_at_node = _get_visits_at_nodes(problem)

    offset_vars = {sid: cp.Variable(name=f"offset_{sid}", nonneg=True) for sid in services}

    def raw_arrival(sid, k, node_id):
        service = services[sid]
        node = nodes[node_id]
        headway = problem.get_service_headway(sid)
        trip_time = service.trip_time_to_node_seconds(node)
        return offset_vars[sid] + headway * k + trip_time

    # Allocate all binary variables as vectors to avoid CVXPY scalar bug.
    num_pairs = _count_visit_pairs(visits_at_node)
    num_wraps = _count_wrap_variables(visits_at_node)
    z_vec = cp.Variable(max(num_pairs, 1), boolean=True, name="z") if num_pairs > 0 else None
    w_vec = cp.Variable(max(num_wraps, 1), boolean=True, name="w") if num_wraps > 0 else None
    z_idx = 0
    w_idx = 0

    constraints = []

    first_sid = next(iter(services))
    constraints.append(offset_vars[first_sid] == 0)

    for sid in services:
        headway = problem.get_service_headway(sid)
        constraints.append(offset_vars[sid] <= headway)

    min_gap_vars = {}

    for node_id, visits in visits_at_node.items():
        n = len(visits)
        min_gap = cp.Variable(name=f"min_gap_{node_id}", nonneg=True)
        min_gap_vars[node_id] = min_gap

        # For each visit, introduce a binary wrap variable so that canonical
        # arrivals live in [0, period). This correctly handles services whose
        # raw arrival times exceed one period at shared nodes.
        canon = {}
        for v_idx, (sid, k) in enumerate(visits):
            raw = raw_arrival(sid, k, node_id)
            w = w_vec[w_idx]
            w_idx += 1
            ca = raw - w * period
            constraints.append(ca >= 0)
            constraints.append(ca <= period - 1)
            canon[(sid, k)] = ca

        # Wrap-around gap via first/last canonical arrival.
        first_arr = cp.Variable(name=f"first_{node_id}")
        last_arr = cp.Variable(name=f"last_{node_id}")
        for key in canon:
            constraints.append(first_arr <= canon[key])
            constraints.append(last_arr >= canon[key])
        constraints.append(first_arr + period - last_arr >= min_gap)

        for i in range(n):
            for j in range(i + 1, n):
                v_i = visits[i]
                v_j = visits[j]
                a_i = canon[v_i]
                a_j = canon[v_j]

                z = z_vec[z_idx]
                z_idx += 1
                # z=1 => i before j; z=0 => j before i (in canonical time)
                constraints.append(a_i + exclusion - a_j <= M * (1 - z))
                constraints.append(a_j + exclusion - a_i <= M * z)
                constraints.append(a_j - a_i >= min_gap - M * (1 - z))
                constraints.append(a_i - a_j >= min_gap - M * z)

    if not min_gap_vars:
        return {sid: 0 for sid in services}

    objective = cp.Maximize(cp.sum(list(min_gap_vars.values())))
    prob = cp.Problem(objective, constraints)
    prob.solve()

    if prob.status in ("infeasible", "unbounded"):
        raise ValueError(f"Solver returned status: {prob.status}")

    offsets = {sid: round(var.value) for sid, var in offset_vars.items()}

    if debug:
        print("---------")
        for node_id, visits in visits_at_node.items():
            arrivals = []
            for sid, k in visits:
                service = services[sid]
                node = nodes[node_id]
                headway = problem.get_service_headway(sid)
                trip_time = service.trip_time_to_node_seconds(node)
                arr = (offsets[sid] + headway * k + trip_time) % period
                arrivals.append(arr)
            arrivals.sort()
            print(node_id, [a // 60 for a in arrivals])

    return offsets
