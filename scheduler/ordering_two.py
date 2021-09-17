from dataclasses import dataclass
from functools import cached_property
from scheduler import scheduling_problem
from scheduler.ordering import proposed_dispatch_excludes_others
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

    def remaining_trips_for_service(self, service_id):
        return self.trips_per_period_dict.get(service_id)

    def remaining_trips(self):
        total = 0
        for service in self.trips_per_period_dict.keys():
            total += self.remaining_trips_for_service(service)
        return total

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


def last_index_of(sequence: List[str], service: str):
    return len(sequence) - sequence[::-1].index(service) - 1


def minimum_time_spanned_by_dispatch_sequence(
    dispatch_sequence: List[str],
    problem: SchedulingProblem,
):
    now = 0
    previous_minimum_times = {}
    for dispatch in dispatch_sequence:
        previous_minimum_time = previous_minimum_times.get(dispatch)
        min_now = now + problem.dispatch_spacing_time
        if previous_minimum_time is not None:
            now = max(min_now, previous_minimum_time + problem.get_service_headway(dispatch))
        else:
            now = min_now
        previous_minimum_times[dispatch] = now
    return now


def proposed_dispatch_is_too_late(sequence: List[str], dispatch: str, problem: SchedulingProblem):
    headway = problem.get_service_headway(dispatch)
    try:
        previous_dispatch_idx = last_index_of(sequence, dispatch)
        other_dispatches_since_previous = sequence[previous_dispatch_idx + 1 :]
        min_time_since_last = minimum_time_spanned_by_dispatch_sequence(
            other_dispatches_since_previous,
            problem,
        )
        return min_time_since_last > headway
    except ValueError:
        return False


def minimum_time_required_to_dispatch_remaining_trains(
    service_pool: ServicePool,
    problem: SchedulingProblem,
):
    remaining_trips = service_pool.remaining_trips()
    min_time = problem.dispatch_spacing_time * max(0, remaining_trips - 1)
    for service in problem.services:
        remaining_trips = service_pool.remaining_trips_for_service(service)
        headway = problem.get_service_headway(service)
        min_time_for_service = (remaining_trips - 1) * headway
        min_time = max(min_time, min_time_for_service)
    return min_time


def get_feasible_dispatch_sequences(problem: SchedulingProblem):
    @listify
    def subproblem(sequence: Tuple[str], pool: ServicePool):
        if pool.remaining_trips() == 0:
            yield sequence
        else:
            for next_pool, next_dispatch in pool.next_candidates():
                next_sequence = sequence + (next_dispatch,)
                min_elapsed = minimum_time_spanned_by_dispatch_sequence(next_sequence, problem)
                min_remaining = minimum_time_required_to_dispatch_remaining_trains(
                    next_pool,
                    problem,
                )
                if min_elapsed + min_remaining > problem.period:
                    continue
                if proposed_dispatch_is_too_late(sequence, next_dispatch, problem):
                    continue
                for resulting_ordering in subproblem(
                    next_sequence,
                    next_pool,
                ):
                    yield resulting_ordering

    return list(set(subproblem(tuple(), ServicePool(problem.trips_per_period))))[0:10]
