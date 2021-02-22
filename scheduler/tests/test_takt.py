from scheduler.takt import get_takt_offsets_for_tph


def test_get_simple_takt_ordering():
    tph = {"a": 2, "b": 2}
    offsets = get_takt_offsets_for_tph(tph)
    assert offsets == {"a": 0, "b": 900}


def test_get_complex_takt_ordering():
    tph = {"a": 4, "b": 3, "c": 2}
    offsets = get_takt_offsets_for_tph(tph)
    assert offsets == {"a": 0, "b": 400, "c": 1200}


def test_get_takt_ordering_with_memory():
    tph = {"a": 4, "b": 4}
    recent_arrival_offsets = {"a": -4 * 60, "b": -15 * 60}
    offsets = get_takt_offsets_for_tph(tph, recent_arrival_offsets)
    assert offsets == {"a": 11 * 60, "b": 0}


def test_get_takt_ordering_with_partial_memory():
    tph = {"a": 4, "b": 4, "c": 2}
    recent_arrival_offsets = {"a": -4 * 60, "b": -15 * 60}
    offsets = get_takt_offsets_for_tph(tph, recent_arrival_offsets)
    assert offsets == {"a": 11 * 60, "b": 0, "c": 360}
