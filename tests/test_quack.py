from schroedinteger import schroedinteger


def test_schroedinteger_is_int():
    x = schroedinteger([1, 2, 3])
    assert isinstance(x, int)
    assert type(x) != int


def test_int_schroedinteger_is_really_int():
    x = schroedinteger([1, 2, 3])
    assert type(int(x)) == int
