from hypothesis import given, assume
from tests.common import mixed_integers
import pytest
import operator


commutative_operators = [
    operator.add, operator.mul, operator.and_, operator.or_, operator.xor
]

associative_operators = commutative_operators

binary_operators = commutative_operators + [
    operator.rshift, operator.truediv
]

embiggening_operators = [operator.lshift, operator.pow]

arithmetic_errors = (ZeroDivisionError, ValueError, OverflowError)


@pytest.mark.parametrize('op', binary_operators)
@given(mixed_integers, mixed_integers)
def test_binary_operators_agree_1(op, x, y):
    try:
        assert op(x, y) == op(int(x), int(y))
    except arithmetic_errors:
        assume(False)


@pytest.mark.parametrize('op', binary_operators)
@given(mixed_integers, mixed_integers)
def test_binary_operators_agree_2(op, x, y):
    try:
        assert op(int(x), int(y)) == op(x, y)
    except arithmetic_errors:
        assume(False)


@pytest.mark.parametrize('op', embiggening_operators)
@given(mixed_integers, mixed_integers)
def test_embiggening_agrees(op, x, y):
    assume(0 <= y <= 100)
    assert op(x, y) == op(int(x), int(y))


@pytest.mark.parametrize('op', commutative_operators)
@given(mixed_integers, mixed_integers)
def test_commutativity(op, x, y):
    assert op(x, y) == op(y, x)


@pytest.mark.parametrize('op', associative_operators)
@given(mixed_integers, mixed_integers, mixed_integers)
def test_associativity(op, x, y, z):
    assert op(op(x, y), z) == op(x, op(y, z))
