from dataclasses import dataclass
import functools
from typing import Dict, List, Tuple, Optional

from synthesize.util import listify, get_pairs

Tph = Dict[str, int]
TaktOrdering = List[Tuple[str, float, float]]
TaktOffsets = Dict[str, float]


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


class SubOrderingPool(ServicePool):
    def __init__(self, sub_orders):
        self.sub_orders = sub_orders

    def next_candidates(self):
        for idx, order in enumerate(self.sub_orders):
            if len(order) > 0:
                first, rest = order[0], order[1:]
                next_array = [rest if o == order else o for o in self.sub_orders]
                yield SubOrderingPool(next_array), first, len(rest) == 0


@dataclass(frozen=True, eq=True)
class Range:
    start: int
    end: int

    def intersect(self, other: "Range") -> "Range":
        start = max(self.start, other.start)
        end = min(self.end, other.end)
        if start < end:
            return Range(start, end)
        return None

    def offset(self, number: int) -> "Range":
        return Range(self.start + number, self.end + number)

    def bound_below(self, number: int) -> "Range":
        start = max(self.start, number)
        end = self.end
        if start < end:
            return Range(start, end)
        return None


@dataclass
class OrderingProblem:
    offset_constraint_ranges_s: Dict[str, Range]
    journey_times_s: Dict[str, int]
    exclusion_time_s: int
    tph: Dict[str, int] = None
    sub_orders: List[List[str]] = None

    @functools.cached_property
    def headways_s(self):
        res = {}
        for key, value in self.tph.items():
            res[key] = HOUR // value
        return res

    @functools.cached_property
    def total_arrivals(self):
        total = 0
        for value in self.tph.values():
            total += value
        return total


def get_next_arrival_time_range(
    headway: int,
    journey_time: int,
    constraint_range: Optional[Range],
    previous_range: Optional[Range],
):
    if previous_range:
        return previous_range.offset(headway)
    elif constraint_range:
        return constraint_range.offset(journey_time)
    else:
        return Range(0, HOUR)


@listify
def _candidates_for_next_arrival(
    now: Range,
    problem: OrderingProblem,
    pool: ServicePool,
    recent_arrivals_by_service_id: Dict[str, Range],
) -> List[str]:
    for next_pool, service_id, is_last in pool.next_candidates():
        journey_time = problem.journey_times_s[service_id]
        headway = problem.headways_s[service_id]
        arrival_range = get_next_arrival_time_range(
            headway=headway,
            journey_time=journey_time,
            constraint_range=problem.offset_constraint_ranges_s.get(service_id),
            previous_range=recent_arrivals_by_service_id.get(service_id),
        )
        if arrival_range:
            meets_is_last_criterion = not is_last or (
                Range(now.end - headway, now.end).intersect(arrival_range)
            )
            if meets_is_last_criterion and now.intersect(arrival_range):
                yield arrival_range, next_pool, service_id


@listify
def _ordering_subproblem(
    now: Range,
    remaining_length: int,
    problem: OrderingProblem,
    pool: ServicePool,
    recent_arrivals_by_service_id: Dict[str, float],
):
    if remaining_length == 0:
        yield []
        return
    candidates = _candidates_for_next_arrival(now, problem, pool, recent_arrivals_by_service_id)
    for arrival, next_pool, service_id in candidates:
        if remaining_length == 1 and service_id == 'a':
            print(remaining_length, service_id, now, arrival)
        head = [service_id]
        next_recent_arrivals_by_service_id = {**recent_arrivals_by_service_id, service_id: arrival}
        tails = _ordering_subproblem(
            now=now.bound_below(arrival.start + problem.exclusion_time_s),
            remaining_length=remaining_length - 1,
            problem=problem,
            pool=next_pool,
            recent_arrivals_by_service_id=next_recent_arrivals_by_service_id,
        )
        for tail in tails:
            yield head + tail


def get_hour_range(problem: OrderingProblem) -> Range:
    min_journey_time = float("inf")
    for time in problem.journey_times_s.values():
        min_journey_time = min(min_journey_time, time)
    return Range(0, HOUR).offset(min_journey_time)


def get_orderings(problem: OrderingProblem) -> TaktOrdering:
    orders = _ordering_subproblem(
        now=get_hour_range(problem),
        remaining_length=problem.total_arrivals,
        problem=problem,
        pool=TphPool(problem.tph),
        recent_arrivals_by_service_id={},
    )
    return [o for o in orders if len(o) == problem.total_arrivals]
