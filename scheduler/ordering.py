from dataclasses import dataclass
from functools import cached_property
from typing import List, Dict, Tuple

from synthesize.util import listify
from scheduler.network import Service, Node
from scheduler.scheduling_problem import SchedulingProblem


@dataclass
class Range:
    lower: int
    upper: int

    def intersection(self, other: "Range"):
        if self.lower > other.upper or other.lower > self.upper:
            return None
        lower_bound = max(self.lower, other.lower)
        upper_bound = min(self.upper, other.upper)
        if lower_bound == upper_bound:
            return None
        return Range(lower_bound, upper_bound)

    def offset(self, n: int):
        return Range(lower=self.lower + n, upper=self.upper + n)

    @cached_property
    def is_empty(self):
        return self.lower == self.upper

    def __repr__(self):
        return f"<{self.lower}, {self.upper}>"


@dataclass
class Arrival:
    service_id: str
    range: Range

    def __repr__(self):
        return f"{self.service_id}@{self.range}"


class ServicePool:
    def __init__(self, trips_per_period_dict):
        self.trips_per_period_dict = trips_per_period_dict

    def next_candidates(self):
        for key, count in self.trips_per_period_dict.items():
            if count > 0:
                next_count = count - 1
                next_dict = {**self.trips_per_period_dict, key: next_count}
                yield ServicePool(next_dict), key


@dataclass
class OrderingState:
    dispatch_ordering: List[str]
    arrival_orderings: List[Dict[str, List[Arrival]]]
    service_pool: ServicePool
    finished: bool = False


@dataclass
class Ordering:
    dispatch_ordering: List[Service]
    arrival_orderings: Dict[Node, List[Tuple[int, Service]]]


def get_arrival_constraint_range(
    ordered_arrivals_of_previous_dispatches: List[Arrival],
    arrival_service_id: str,
    node_id: str,
    problem: SchedulingProblem,
    debug: bool,
):
    headway = problem.get_service_headway(arrival_service_id)
    trip_time = problem.trip_time_to_node(arrival_service_id, node_id)
    existing_arrival_for_service_id = next(
        (a for a in reversed(ordered_arrivals_of_previous_dispatches) if a.service_id == arrival_service_id),
        None,
    )
    if existing_arrival_for_service_id:
        return existing_arrival_for_service_id.range.offset(headway)
    return Range(trip_time, trip_time + headway)


def minimum_time_spanned_by_sequence(sequence: List[str], problem: SchedulingProblem):
    now = 0
    previous_minimum_times = {}
    for dispatch in sequence:
        previous_minimum_time = previous_minimum_times.get(dispatch)
        min_now = now + problem.dispatch_spacing_time
        if previous_minimum_time is not None:
            now = max(min_now, previous_minimum_time + problem.get_service_headway(dispatch))
        else:
            now = min_now
        previous_minimum_times[dispatch] = now
    return now


def last_index_of(sequence: List[str], service: str):
    return len(sequence) - sequence[::-1].index(service) - 1


def proposed_dispatch_is_too_late(sequence: List[str], dispatch: str, problem: SchedulingProblem):
    headway = problem.get_service_headway(dispatch)
    try:
        previous_dispatch_idx = last_index_of(sequence, dispatch)
        other_dispatches_since_previous = sequence[previous_dispatch_idx + 1 :]
        min_time_since_last = minimum_time_spanned_by_sequence(other_dispatches_since_previous, problem)
        return min_time_since_last > headway
    except ValueError:
        return False


def sequence_cannot_be_cyclical(sequence: List[str], problem: SchedulingProblem):
    for service_id in problem.services.keys():
        headway = problem.get_service_headway(service_id)
        last_index = last_index_of(sequence, service_id)
        dispatches_since_last = sequence[last_index + 1 :]
        min_time_since_last = minimum_time_spanned_by_sequence(dispatches_since_last, problem)
        if min_time_since_last > headway:
            return True
    return False


def get_earliest_feasible_dispatch_time(
    ordered_arrivals_of_previous_dispatches: List[Arrival],
    arrival_service_id: str,
    node_id: str,
    problem: SchedulingProblem,
):
    if problem.is_dispatching_node(arrival_service_id, node_id):
        dispatched_services_from_node = problem.dispatched_services_for_node_id(node_id)
        latest_dispatch = next(
            (
                a
                for a in reversed(ordered_arrivals_of_previous_dispatches)
                if a.service_id in dispatched_services_from_node
            ),
            None,
        )
        if latest_dispatch:
            return latest_dispatch.range.lower + problem.dispatch_spacing_time
    return 0


def constrain_arrival_range_for_dispatch_headways(
    ordered_arrivals_of_previous_dispatches: List[Arrival],
    arrival_range: Range,
    arrival_service_id: str,
    node_id: str,
    problem: SchedulingProblem,
    debug: bool,
):
    if problem.is_dispatching_node(arrival_service_id, node_id):
        headway = problem.get_service_headway(arrival_service_id)
        services_arriving_at_node = problem.dispatched_services_for_node_id(node_id)
        latest_arrival_of_service = next(
            (a for a in reversed(ordered_arrivals_of_previous_dispatches) if a.service_id == arrival_service_id),
            None,
        )
        latest_arrival_of_any_service = next(
            (a for a in reversed(ordered_arrivals_of_previous_dispatches) if a.service_id in services_arriving_at_node),
            None,
        )
        if latest_arrival_of_any_service:
            earliest_possible_dispatch_time = latest_arrival_of_any_service.range.lower + problem.dispatch_spacing_time
            if latest_arrival_of_service:
                minimum_time_since_latest_dispatch = (
                    earliest_possible_dispatch_time - latest_arrival_of_service.range.lower
                )
                if minimum_time_since_latest_dispatch > headway:
                    return None
            return arrival_range.intersection(Range(earliest_possible_dispatch_time, float("inf")))
    return arrival_range


def get_feasible_arrival_range_at_node(
    ordered_arrivals_of_previous_dispatches: List[Arrival],
    arrival_service_id: str,
    node_id: str,
    problem: SchedulingProblem,
    debug: bool,
):
    arrival_range = get_arrival_constraint_range(
        ordered_arrivals_of_previous_dispatches,
        arrival_service_id,
        node_id,
        problem,
        debug,
    )
    dispatch_range = constrain_arrival_range_for_dispatch_headways(
        ordered_arrivals_of_previous_dispatches,
        arrival_range,
        arrival_service_id,
        node_id,
        problem,
        debug,
    )
    return dispatch_range


@listify
def get_possible_insertions_of_dispatch_or_arrival(
    ordered_arrivals_of_previous_dispatches: List[Arrival],
    arrival_service_id: str,
    node_id: str,
    problem: SchedulingProblem,
    debug: bool,
) -> List[Tuple[Range, List[Arrival]]]:
    feasible_range = get_feasible_arrival_range_at_node(
        ordered_arrivals_of_previous_dispatches,
        arrival_service_id,
        node_id,
        problem,
        debug,
    )
    if not feasible_range:
        return
    for idx in range(1 + len(ordered_arrivals_of_previous_dispatches)):
        boundary_above = (
            float("inf")
            if idx == len(ordered_arrivals_of_previous_dispatches)
            else ordered_arrivals_of_previous_dispatches[idx].range.lower
        )
        boundary_below = 0 if idx == 0 else ordered_arrivals_of_previous_dispatches[idx - 1].range.lower
        boundary_range = Range(boundary_below, boundary_above)
        insertion_range = boundary_range.intersection(feasible_range)
        if insertion_range:
            arrival = Arrival(service_id=arrival_service_id, range=insertion_range)
            insertion_list = list(ordered_arrivals_of_previous_dispatches)
            insertion_list.insert(idx, arrival)
            yield insertion_range, insertion_list


def get_arrival_orderings_for_dispatch(state: OrderingState, problem: SchedulingProblem, dispatch_service_id: str):
    @listify
    def subproblem(
        node_ids: List[str],
        existing_arrivals: Dict[str, List[Arrival]],
        previous_range_at_trip_time: Tuple[int, Range] = None,
    ):
        if len(node_ids) == 0:
            yield {}
            return
        node_id, rest_node_ids = node_ids[0], node_ids[1:]
        trip_time_at_node = problem.trip_time_to_node(dispatch_service_id, node_id)
        existing_arrivals_at_node = existing_arrivals.get(node_id) or []
        possible_insertions = get_possible_insertions_of_dispatch_or_arrival(
            ordered_arrivals_of_previous_dispatches=existing_arrivals_at_node,
            arrival_service_id=dispatch_service_id,
            node_id=node_id,
            problem=problem,
            debug=False,
        )
        constraining_range = None
        if previous_range_at_trip_time:
            (
                trip_time_at_previous_node,
                previous_node_range,
            ) = previous_range_at_trip_time
            offset_time = trip_time_at_node - trip_time_at_previous_node
            constraining_range = previous_node_range.offset(offset_time)
        for insertion_range, insertion_order in possible_insertions:
            resulting_range = (
                constraining_range.intersection(insertion_range) if constraining_range else insertion_range
            )
            if resulting_range:
                for partial in subproblem(
                    node_ids=rest_node_ids,
                    existing_arrivals=existing_arrivals,
                    previous_range_at_trip_time=(trip_time_at_node, resulting_range),
                ):
                    yield {**partial, node_id: insertion_order}

    node_ids_in_service = problem.node_ids_for_service_id(dispatch_service_id)
    next_arrival_orderings = []
    for arrival_ordering in state.arrival_orderings:
        for ordering in subproblem(node_ids=node_ids_in_service, existing_arrivals=arrival_ordering):
            next_arrival_orderings.append({**arrival_ordering, **ordering})
    return next_arrival_orderings


@listify
def get_next_ordering_states(state: OrderingState, problem: SchedulingProblem):
    for next_pool, candidate_service_id in state.service_pool.next_candidates():
        if proposed_dispatch_is_too_late(state.dispatch_ordering, candidate_service_id, problem):
            continue
        next_arrival_orderings = get_arrival_orderings_for_dispatch(
            state=state, problem=problem, dispatch_service_id=candidate_service_id
        )
        next_dispatch_ordering = state.dispatch_ordering + [candidate_service_id]
        if len(next_arrival_orderings) > 0:
            yield OrderingState(
                dispatch_ordering=next_dispatch_ordering,
                arrival_orderings=next_arrival_orderings,
                service_pool=next_pool,
                finished=len(next_dispatch_ordering) == problem.total_dispatches,
            )


def get_orderings_from_ordering_state(state: OrderingState, problem: SchedulingProblem):
    dispatch_ordering_of_services = []
    for service_id in state.dispatch_ordering:
        service = problem.services[service_id]
        if service not in dispatch_ordering_of_services:
            dispatch_ordering_of_services.append(service)
    for arrival_ordering in state.arrival_orderings:
        arrival_orderings_of_nodes = {}
        for node_id, arrivals_at_node in arrival_ordering.items():
            node = problem.nodes[node_id]
            service_id_indices = {}
            arrival_tuples = []
            for arrival in arrivals_at_node:
                index = service_id_indices.setdefault(arrival.service_id, 0)
                service_id_indices[arrival.service_id] += 1
                service = problem.services[arrival.service_id]
                arrival_tuple = (index, service)
                arrival_tuples.append(arrival_tuple)
            arrival_orderings_of_nodes[node] = arrival_tuples
        yield Ordering(
            dispatch_ordering=dispatch_ordering_of_services,
            arrival_orderings=arrival_orderings_of_nodes,
        )


@listify
def get_orderings(problem: SchedulingProblem):
    service_pool = ServicePool(problem.trips_per_period)
    initial_state = OrderingState(dispatch_ordering=[], arrival_orderings=[{}], service_pool=service_pool)

    def subproblem(state: OrderingState):
        if state.finished and not sequence_cannot_be_cyclical(state.dispatch_ordering, problem):
            return [state]
        else:
            results = []
            next_states = get_next_ordering_states(state, problem)
            for next_state in next_states:
                results += subproblem(next_state)
            return results

    ordering_states = subproblem(initial_state)
    for state in ordering_states:
        for ordering in get_orderings_from_ordering_state(state, problem):
            yield ordering
