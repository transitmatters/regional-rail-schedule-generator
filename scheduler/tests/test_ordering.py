from scheduler.ordering import get_orderings, OrderingProblem


def test_ordering_with_tph():
    problem = OrderingProblem(
        tph={"a": 2, "b": 2},
        exclusion_time_s=60,
    )
    orderings = get_orderings(problem)
    assert orderings == [["a", "b", "a", "b"], ["b", "a", "b", "a"]]


def test_ordering_with_sub_sequences():
    problem = OrderingProblem(
        tph={
            "a": 2,
            "b": 2,
            "c": 2,
        },
        sub_sequences=[["a", "b", "a", "b"], ["c", "c"]],
        exclusion_time_s=60,
    )
    orderings = get_orderings(problem)
    assert orderings == [
        ["a", "b", "c", "a", "b", "c"],
        ["a", "c", "b", "a", "c", "b"],
        ["c", "a", "b", "c", "a", "b"],
    ]


def test_ordering_with_sub_sequences_and_order_constraints():
    problem = OrderingProblem(
        tph={
            "a": 2,
            "b": 2,
            "c": 4,
        },
        sub_sequences=[["a", "b", "a", "b"], ["c", "c", "c", "c"]],
        order_constraints=[("c", "a"), ("c", "b")],
        exclusion_time_s=60,
    )
    orderings = get_orderings(problem)
    assert orderings == [
        ["c", "a", "b", "c", "a", "b", "c", "c"],
        ["c", "a", "b", "c", "a", "c", "b", "c"],
        ["c", "a", "b", "c", "c", "a", "b", "c"],
        ["c", "a", "c", "b", "a", "c", "b", "c"],
        ["c", "a", "c", "b", "a", "c", "c", "b"],
        ["c", "a", "c", "b", "c", "a", "b", "c"],
        ["c", "a", "c", "b", "c", "a", "c", "b"],
        ["c", "a", "c", "c", "b", "a", "c", "b"],
        ["c", "c", "a", "b", "c", "a", "b", "c"],
        ["c", "c", "a", "b", "c", "a", "c", "b"],
        ["c", "c", "a", "b", "c", "c", "a", "b"],
        ["c", "c", "a", "c", "b", "a", "c", "b"],
        ["c", "c", "a", "c", "b", "c", "a", "b"],
        ["c", "c", "c", "a", "b", "c", "a", "b"],
    ]
