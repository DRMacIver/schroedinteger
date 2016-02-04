from schroedinteger import schroedinteger
from tests.common import schroedintegers
from hypothesis import given


def test_schroedinteger_is_int():
    x = schroedinteger([1, 2, 3])
    assert isinstance(x, int)
    assert type(x) != int


def test_int_schroedinteger_is_really_int():
    x = schroedinteger([1, 2, 3])
    assert type(int(x)) == int


@given(schroedintegers)
def test_hashes_the_same(x):
    assert hash(x) == hash(int(x))
