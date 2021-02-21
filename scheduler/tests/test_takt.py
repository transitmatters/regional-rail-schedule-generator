from scheduler.takt import get_takt_ordering_for_tph


def _assert_ordering(ordering, service_ids):
    assert "".join([a[0] for a in ordering]) == service_ids


def test_get_simple_takt_ordering_for_headways():
    tph = {"a": 2, "b": 2}
    ordering = get_takt_ordering_for_tph(tph)
    _assert_ordering(ordering, "abab")


def test_get_complex_takt_ordering_for_headways():
    tph = {"a": 4, "b": 3, "c": 2}
    ordering = get_takt_ordering_for_tph(tph)
    _assert_ordering(ordering, "bacbaabca")
