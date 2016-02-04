from hypothesis import strategies as st
from hypothesis import given, assume
from bisect import bisect_left
from schroedinteger import schroedinteger

from tests.common import schroedintegers


@given(st.lists(st.integers()), schroedintegers)
def test_bisection_agrees_with_eventual_answer(ls, x):
    i = bisect_left(ls, x)
    assert i == bisect_left(ls, int(x))


@given(st.lists(schroedintegers))
def test_sorting_produces_eventual_sort(ls):
    ls.sort()
    forced = list(map(int, ls))
    assert forced == sorted(forced)


@given(st.random_module(), st.lists(st.integers(), min_size=1))
def test_can_produce_different_results(rnd, ls):
    assume(len(set(bisect_left(ls, i) for i in ls)) > 1)
    seen = set()
    for _ in range(100):
        x = schroedinteger(ls)
        seen.add(bisect_left(ls, x))
        if len(seen) > 1:
            return
    assert False


@given(schroedintegers, schroedintegers)
def test_equal_integers_give_equal_values(x, y):
    assume(x == y)
    assert int(x) == int(y)


@given(schroedintegers, schroedintegers)
def test_distinct_integers_give_distinct_values(x, y):
    assume(x != y)
    assert int(x) != int(y)
