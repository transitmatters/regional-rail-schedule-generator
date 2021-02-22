import functools
from typing import Dict, List, Tuple
from frozendict import frozendict

from synthesize.util import listify, get_pairs

Tph = Dict[str, int]
TaktOrdering = List[Tuple[str, float, float]]
TaktOffsets = Dict[str, float]

HOUR = 3600


@listify
def _candidates_for_next_arrival(
    now: float,
    headways_by_service_id: Dict[str, int],
    arrivals_pool_by_service_id: Dict[str, int],
    recent_arrivals_by_service_id: Dict[str, float],
) -> List[str]:
    for service_id in headways_by_service_id.keys():
        headway = headways_by_service_id[service_id]
        has_remaining_arrival = arrivals_pool_by_service_id[service_id] > 0
        most_recent_arrival = recent_arrivals_by_service_id.get(service_id)
        if has_remaining_arrival:
            if most_recent_arrival is None:
                true_arrival_time = now
            else:
                true_arrival_time = most_recent_arrival + headway
            yield true_arrival_time, service_id


@functools.cache
def _takt_ordering_subproblem(
    now: float,
    takt: float,
    exclusion_time_min: float,
    remaining_length: int,
    headways_by_service_id: Dict[str, float],
    arrivals_pool_by_service_id: Dict[str, int],
    recent_arrivals_by_service_id: Dict[str, float],
):
    if remaining_length == 0:
        return []
    candidate_next_ids = _candidates_for_next_arrival(
        now, headways_by_service_id, arrivals_pool_by_service_id, recent_arrivals_by_service_id
    )
    candidates = []
    for true_arrival_time, service_id in candidate_next_ids:
        head = [(service_id, true_arrival_time, true_arrival_time - now)]
        next_arrivals_pool_by_service_id = arrivals_pool_by_service_id.copy(
            **{service_id: arrivals_pool_by_service_id[service_id] - 1},
        )
        next_recent_arrivals_by_service_id = recent_arrivals_by_service_id.copy(
            **{service_id: true_arrival_time}
        )
        candidate_tail = _takt_ordering_subproblem(
            now=now + takt,
            takt=takt,
            exclusion_time_min=exclusion_time_min,
            remaining_length=remaining_length - 1,
            headways_by_service_id=headways_by_service_id,
            arrivals_pool_by_service_id=next_arrivals_pool_by_service_id,
            recent_arrivals_by_service_id=next_recent_arrivals_by_service_id,
        )
        candidates.append(head + candidate_tail)
    best = min(
        candidates, key=lambda t: _get_ordering_cost(t, remaining_length, exclusion_time_min)
    )
    return best


def _get_initial_values(tph: Tph) -> Dict[str, int]:
    arrivals_pool = {}
    headways = {}
    total_arrivals = 0
    for service_id, trips_per_hour in tph.items():
        total_arrivals += trips_per_hour
        arrivals_pool[service_id] = trips_per_hour
        headways[service_id] = HOUR / trips_per_hour
    takt = HOUR / total_arrivals
    return frozendict(arrivals_pool), frozendict(headways), takt, total_arrivals


def _is_valid_ordering(ordering: TaktOrdering, expected_length: int, exclusion_time_min: float):
    if len(ordering) != expected_length:
        return False
    for (_, t1, _), (_, t2, _) in get_pairs(ordering):
        if t1 >= HOUR or t2 >= HOUR:
            return False
        if t2 - t1 < exclusion_time_min:
            return False
    return True


def _get_ordering_cost(ordering: TaktOrdering, expected_length: int, exclusion_time_min: float):
    if not _is_valid_ordering(ordering, expected_length, exclusion_time_min):
        return float("inf")
    return sum(deviation ** 2 for (_, _, deviation) in ordering)


def _get_takt_offsets_from_ordering(ordering: TaktOrdering) -> TaktOffsets:
    offsets_by_id = {}
    for (service_id, time, _) in ordering:
        if service_id not in offsets_by_id:
            offsets_by_id[service_id] = round(time)
    return offsets_by_id


def get_takt_offsets_for_tph(
    tph: Tph,
    recent_arrival_offsets: TaktOffsets = None,
    exclusion_time_min=1,
) -> TaktOrdering:
    arrivals, headways, takt, total_arrivals = _get_initial_values(tph)
    best_ordering = _takt_ordering_subproblem(
        now=0,
        takt=takt,
        exclusion_time_min=exclusion_time_min,
        remaining_length=total_arrivals,
        headways_by_service_id=headways,
        arrivals_pool_by_service_id=arrivals,
        recent_arrivals_by_service_id=frozendict(recent_arrival_offsets or {}),
    )
    if _is_valid_ordering(best_ordering, total_arrivals, exclusion_time_min):
        offsets = _get_takt_offsets_from_ordering(best_ordering)
        return offsets
