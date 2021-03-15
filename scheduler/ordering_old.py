from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional
from functools import cache, cached_property

from synthesize.util import listify

from scheduler.service_pattern_graph import ServicePatternGraph, ServicePattern

Sequence = Tuple[str]


class ServicePool:
    def __init__(self, trips_per_period_dict):
        self.trips_per_period_dict = trips_per_period_dict

    def next_candidates(self):
        for key, count in self.trips_per_period_dict.items():
            if count > 0:
                next_count = count - 1
                next_dict = {**self.trips_per_period_dict, key: next_count}
                yield ServicePool(next_dict), key, next_count == 0


@dataclass
class OrderingProblem:
    trips_per_period: Dict[str, int]
    exclusion_time_s: int
    period: int
    service_pattern_graph: Optional[ServicePatternGraph]
    strict_order_checking: bool

    @cached_property
    def headways_s(self):
        res = {}
        for key, value in self.trips_per_period.items():
            res[key] = self.period // value
        return res

    @cached_property
    def services(self):
        return self.trips_per_period.keys()

    @cached_property
    def total_dispatches(self):
        total = 0
        for value in self.trips_per_period.values():
            total += value
        return total


def _debug_is_subsequence(seq_str: str, subseq: Sequence):
    return seq_str.startswith("".join(subseq))


def last_index_of(sequence: Sequence, service: str):
    return len(sequence) - sequence[::-1].index(service) - 1


def get_sub_sequence_for_service_pattern(
    sequence: Sequence, service_pattern: ServicePattern
) -> Sequence:
    sub_sequence = []
    for dispatch in sequence:
        if dispatch in service_pattern:
            sub_sequence.append(dispatch)
    return tuple(sub_sequence)


def minimum_time_spanned_by_sequence(sequence: Sequence, problem: OrderingProblem):
    now = 0
    previous_minimum_times = {}
    for dispatch in sequence:
        previous_minimum_time = previous_minimum_times.get(dispatch)
        min_now = now + problem.exclusion_time_s
        if previous_minimum_time is not None:
            now = max(min_now, previous_minimum_time + problem.headways_s[dispatch])
        else:
            now = min_now
        previous_minimum_times[dispatch] = now
    return now


def arrives_too_late(sequence: Sequence, dispatch: str, problem: OrderingProblem):
    headway = problem.headways_s[dispatch]
    try:
        previous_dispatch_idx = last_index_of(sequence, dispatch)
        other_dispatches_since_previous = sequence[previous_dispatch_idx + 1 :]
        min_time_since_last = minimum_time_spanned_by_sequence(
            other_dispatches_since_previous, problem
        )
        return min_time_since_last > headway
    except ValueError:
        return False


def sequence_violates_service_pattern_times(
    sequence: Sequence, dispatch: str, problem: OrderingProblem, service_pattern: ServicePattern
):
    if dispatch in sequence:
        return False
    dispatch_headway = problem.headways_s[dispatch]
    dispatch_travel_time = service_pattern[dispatch]
    max_allowable_time_before_dispatch = dispatch_headway + dispatch_travel_time
    seen_services = set()
    for idx, service in enumerate(sequence):
        if service in seen_services:
            continue
        seen_services.add(service)
        service_headway = problem.headways_s[service]
        service_travel_time = service_pattern[service]
        if problem.strict_order_checking:
            previous_services = sequence[0:idx]
            min_time_before_service = minimum_time_spanned_by_sequence(previous_services, problem)
        else:
            min_time_before_service = 0
        min_time_until_service = service_headway + service_travel_time + min_time_before_service
        if min_time_until_service > max_allowable_time_before_dispatch:
            return True
    return False


def next_dispatch_is_acceptable(sequence: Sequence, dispatch: str, problem: OrderingProblem):
    service_pattern_graph = problem.service_pattern_graph
    if not service_pattern_graph:
        return not arrives_too_late(sequence, dispatch, problem)

    @cache
    def sub_sequence_arrives_too_late(sub_sequence: Sequence):
        return arrives_too_late(sub_sequence, dispatch, problem)

    def sequence_acceptable_by_service_pattern(service_pattern: ServicePattern):
        if dispatch not in service_pattern:
            return True
        sub_sequence = get_sub_sequence_for_service_pattern(sequence, service_pattern)
        too_late = sub_sequence_arrives_too_late(sub_sequence)
        return not too_late and not sequence_violates_service_pattern_times(
            sub_sequence, dispatch, problem, service_pattern
        )

    return service_pattern_graph.accepts(sequence_acceptable_by_service_pattern)


def sequence_cannot_be_cyclical(sequence: Sequence, problem: OrderingProblem):
    for service in problem.services:
        headway = problem.headways_s[service]
        last_index = last_index_of(sequence, service)
        dispatches_since_last = sequence[last_index + 1 :]
        min_time_since_last = minimum_time_spanned_by_sequence(dispatches_since_last, problem)
        if min_time_since_last > headway:
            return True
    return False


@listify
def _candidates_for_next_dispatch(
    sequence: List[str],
    problem: OrderingProblem,
    pool: ServicePool,
) -> List[str]:
    for next_pool, service_id, is_last in pool.next_candidates():
        if next_dispatch_is_acceptable(sequence, service_id, problem):
            yield service_id, next_pool


@listify
def _ordering_subproblem(problem: OrderingProblem, pool: ServicePool, sequence: Sequence):
    if len(sequence) == problem.total_dispatches:
        if not sequence_cannot_be_cyclical(sequence, problem):
            yield sequence
    candidates = _candidates_for_next_dispatch(sequence, problem, pool)
    for service_id, next_pool in candidates:
        next_sequence = sequence + (service_id,)
        results = _ordering_subproblem(problem, next_pool, next_sequence)
        for result in results:
            yield result


def get_plausible_service_orderings(
    trips_per_period: Dict[str, int],
    service_pattern_graph: ServicePatternGraph = None,
    exclusion_time_s: int = 60,
    period: int = 3600,
    strict_order_checking: bool = False,
):
    problem = OrderingProblem(
        trips_per_period=trips_per_period,
        service_pattern_graph=service_pattern_graph,
        period=period,
        exclusion_time_s=exclusion_time_s,
        strict_order_checking=strict_order_checking,
    )
    pool = ServicePool(trips_per_period)
    orders = _ordering_subproblem(problem=problem, pool=pool, sequence=tuple())
    return set(orders)
