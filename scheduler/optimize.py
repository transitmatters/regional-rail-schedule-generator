from typing import List
from dataclasses import dataclass
import cvxpy as cp

from synthesize.util import get_pairs, listify

from scheduler.network import Service, Node
from scheduler.ordering import Ordering
from scheduler.scheduling_problem import SchedulingProblem


@dataclass
class OptimizeContext:
    ordering: Ordering
    problem: SchedulingProblem

    def __post_init__(self):
        self._variables = {}

    def _get_or_create_variable(self, name: str, **kwargs):
        existing = self._variables.get(name)
        if existing:
            return existing
        variable = cp.Variable(name=name, **kwargs)
        self._variables[name] = variable
        return variable

    def get_departure_offset_variable(self, service: Service):
        return self._get_or_create_variable(f"departure_offset_{service}", nonneg=True)


def get_indexed_arrival_expression(
    ctx: OptimizeContext, service: Service, index: int, node: Node
):
    offset = ctx.get_departure_offset_variable(service)
    headway = ctx.problem.get_service_headway(service)
    trip_time = service.trip_time_to_node_seconds(node)
    if trip_time is None:
        raise ValueError("Got invalid trip time")
    return offset + headway * index + trip_time


@listify
def get_ordered_arrival_expressions_for_node(ctx: OptimizeContext, node: Node):
    arrivals_by_id = ctx.ordering.arrival_orderings[node]
    for (index, service) in arrivals_by_id:
        yield get_indexed_arrival_expression(ctx, service, index, node)


@listify
def get_constraints_for_node(ctx: OptimizeContext, node: Node):
    arrival_expressions = get_ordered_arrival_expressions_for_node(ctx, node)
    for arrival_expr_a, arrival_expr_b in get_pairs(arrival_expressions):
        yield arrival_expr_a + ctx.problem.exclusion_time <= arrival_expr_b


def get_global_constraints(ctx: OptimizeContext):
    for idx, service in enumerate(ctx.ordering.dispatch_ordering):
        headway = ctx.problem.get_service_headway(service)
        offset = ctx.get_departure_offset_variable(service)
        if idx == 0:
            yield offset == 0
        else:
            yield offset + 1 <= headway
    for (service_a, service_b) in get_pairs(ctx.ordering.dispatch_ordering):
        offset_a = ctx.get_departure_offset_variable(service_a)
        offset_b = ctx.get_departure_offset_variable(service_b)
        yield offset_a <= offset_b


def get_scheduler_constraints(ctx: OptimizeContext):
    constraints = list(get_global_constraints(ctx))
    for node in ctx.problem.nodes.values():
        constraints += get_constraints_for_node(ctx, node)
    return constraints


def get_objective_for_node(ctx: OptimizeContext, node: Node):
    obj = 0
    total_arrivals = len(ctx.ordering.arrival_orderings[node])
    weight = 1 / total_arrivals
    arrival_exprs = get_ordered_arrival_expressions_for_node(ctx, node)
    desired_headway = ctx.problem.period // total_arrivals
    for (first, second) in get_pairs(arrival_exprs):
        term = ((second - first) - desired_headway) ** 2
        obj += term
    first = arrival_exprs[0]
    last = arrival_exprs[-1]
    term = ((first + ctx.problem.period - last) - desired_headway) ** 2
    return weight * obj


def get_scheduler_objective(ctx: OptimizeContext):
    obj = 0
    for node in ctx.problem.nodes.values():
        obj += get_objective_for_node(ctx, node)
    return obj


def solve_departure_offsets(problem: SchedulingProblem, ordering: Ordering):
    ctx = OptimizeContext(problem=problem, ordering=ordering)
    constraints = get_scheduler_constraints(ctx)
    objective = get_scheduler_objective(ctx)
    cvx_problem = cp.Problem(cp.Minimize(objective), constraints)
    cvx_problem.solve()
    if cvx_problem.status in ["infeasible", "unbounded"]:
        return float("inf"), None, None
    offsets = {}
    arrivals = {}
    for service in problem.services.values():
        departure_offset = ctx.get_departure_offset_variable(service)
        offsets[service.id] = round(departure_offset.value)
    for node in problem.nodes.values():
        exprs = get_ordered_arrival_expressions_for_node(ctx, node)
        arrivals[node.id] = [round(e.value) for e in exprs]
    return cvx_problem.value, offsets, arrivals


def solve_departure_offsets_for_orderings(
    problem: SchedulingProblem,
    orderings: List[Ordering],
    debug=True,
):
    best_offsets = None
    best_arrivals = None
    best_ordering = None
    best_value = float("inf")
    for ordering in orderings:
        value, offsets, arrivals = solve_departure_offsets(problem, ordering)
        if value < best_value:
            best_ordering = ordering
            best_value = value
            best_offsets = offsets
            best_arrivals = arrivals
    if debug:
        print("---------")
        print(best_ordering)
        for node_id, arrivals in best_arrivals.items():
            print(node_id, [a // 60 for a in arrivals])
    return best_offsets
