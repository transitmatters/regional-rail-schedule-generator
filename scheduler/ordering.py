from dataclasses import dataclass
from typing import Dict, List, Tuple
import functools

from synthesize.util import listify

Sequence = List[str]
ArrivalOrderConstraint = Tuple[str, str]

HOUR = 3600


class ServicePool:
    def next_candidates(self):
        raise NotImplementedError()


class TphPool(ServicePool):
    def __init__(self, tph_dict):
        self.tph_dict = tph_dict

    def next_candidates(self):
        for key, count in self.tph_dict.items():
            if count > 0:
                next_count = count - 1
                next_dict = {**self.tph_dict, key: next_count}
                yield TphPool(next_dict), key, next_count == 0


class SubSequencePool(ServicePool):
    def __init__(self, sub_sequences):
        self.sub_sequences = sub_sequences

    def next_candidates(self):
        for idx, order in enumerate(self.sub_sequences):
            if len(order) > 0:
                first, rest = order[0], order[1:]
                next_array = [rest if o is order else o for o in self.sub_sequences]
                yield SubSequencePool(next_array), first, len(rest) == 0


@dataclass
class OrderingProblem:
    exclusion_time_s: int
    tph: Dict[str, int]
    sub_sequences: List[Sequence] = None
    order_constraints: List[ArrivalOrderConstraint] = None

    @functools.cached_property
    def headways_s(self):
        res = {}
        for key, value in self.tph.items():
            res[key] = HOUR // value
        return res

    @functools.cached_property
    def services(self):
        return self.tph.keys()

    @functools.cached_property
    def total_arrivals(self):
        total = 0
        for value in self.tph.values():
            total += value
        return total


def _debug_is_subsequence(seq_str: str, subseq: Sequence):
    return seq_str.startswith("".join(subseq))


def last_index_of(sequence: Sequence, service: str):
    return len(sequence) - sequence[::-1].index(service) - 1


def can_arrive(sequence: Sequence, arrival: str, order_constraints: List[ArrivalOrderConstraint]):
    if order_constraints:
        for (before, after) in order_constraints:
            if after == arrival and before not in sequence:
                return False
    return True


def minimum_time_spanned_by_sequence(sequence: Sequence, problem: OrderingProblem):
    now = 0
    previous_minimum_times = {}
    for arrival in sequence:
        previous_minimum_time = previous_minimum_times.get(arrival)
        min_now = now + problem.exclusion_time_s
        if previous_minimum_time is not None:
            now = max(min_now, previous_minimum_time + problem.headways_s[arrival])
        else:
            now = min_now
        previous_minimum_times[arrival] = now
    return now


def arrives_too_late(sequence: Sequence, arrival: str, problem: OrderingProblem):
    headway = problem.headways_s[arrival]
    try:
        previous_arrival_idx = last_index_of(sequence, arrival)
        other_arrivals_since_previous = sequence[previous_arrival_idx + 1 :]
        min_time_since_last = minimum_time_spanned_by_sequence(
            other_arrivals_since_previous, problem
        )
        return min_time_since_last > headway
    except ValueError:
        return False


def sequence_cannot_be_cyclical(sequence: Sequence, problem: OrderingProblem):
    for service in problem.services:
        headway = problem.headways_s[service]
        last_index = last_index_of(sequence, service)
        arrivals_since_last = sequence[last_index + 1 :]
        min_time_since_last = minimum_time_spanned_by_sequence(arrivals_since_last, problem)
        if min_time_since_last > headway:
            return True
    return False


@listify
def _candidates_for_next_arrival(
    sequence: List[str],
    problem: OrderingProblem,
    pool: ServicePool,
) -> List[str]:
    for next_pool, service_id, is_last in pool.next_candidates():
        if can_arrive(sequence, service_id, problem.order_constraints):
            if not arrives_too_late(sequence, service_id, problem):
                yield service_id, next_pool


@listify
def _ordering_subproblem(
    problem: OrderingProblem,
    pool: ServicePool,
    sequence: List[str],
):
    if len(sequence) == problem.total_arrivals:
        if not sequence_cannot_be_cyclical(sequence, problem):
            yield sequence
    candidates = _candidates_for_next_arrival(sequence, problem, pool)
    for service_id, next_pool in candidates:
        next_sequence = sequence + [service_id]
        results = _ordering_subproblem(problem, next_pool, next_sequence)
        for result in results:
            yield result


def get_orderings(problem: OrderingProblem):
    pool = SubSequencePool(problem.sub_sequences) if problem.sub_sequences else TphPool(problem.tph)
    orders = _ordering_subproblem(problem=problem, pool=pool, sequence=[])
    return orders
