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


def test_has_same_methods():
    x = 1
    y = schroedinteger([1, 2])

    for v in dir(x):
        assert hasattr(y, v)
