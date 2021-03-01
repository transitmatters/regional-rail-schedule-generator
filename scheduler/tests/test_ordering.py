from scheduler.ordering import get_orderings, OrderingProblem, Range


# def test_ordering():
#     problem = OrderingProblem(
#         tph={"a": 2, "c": 2},
#         journey_times_s={"a": 20 * 60, "c": 40 * 60},
#         offset_constraint_ranges_s={"a": Range(0, 15 * 60), "c": Range(0, 30 * 60)},
#         exclusion_time_s=60,
#     )
#     orderings = get_orderings(problem)
#     assert orderings == [["a", "a", "c", "c"], ["a", "c", "a", "c"]]


def test_ordering_with_no_prior_constraints():
    problem = OrderingProblem(
        tph={"a": 2, "b": 2},
        journey_times_s={"a": 0, "b": 0, "c": 0},
        offset_constraint_ranges_s={},
        exclusion_time_s=60,
    )
    orderings = get_orderings(problem)
    print(orderings)
    assert 1 == 2
