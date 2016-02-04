from tests.common import schroedintegers
from hypothesis import given


@given(schroedintegers)
def test_has_same_bit_length(x):
    assert x.bit_length() == int(x).bit_length()
