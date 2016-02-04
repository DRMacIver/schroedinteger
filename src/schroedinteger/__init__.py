# coding=utf-8

# This file is part of schroedinteger
# https://github.com/DRMacIver/schroedinteger)

# Most of this work is copyright (C) 2013-2015 David R. MacIver
# (david@drmaciver.com), but it contains contributions by others, who hold
# copyright over their individual contributions.

# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, You can
# obtain one at http://mozilla.org/MPL/2.0/.

# END HEADER

import z3
import operator
import random


class SharedSolver(object):
    def __init__(self):
        self.solver = z3.Solver()

    def merge(self, other):
        if self.solver is other.solver:
            return
        for a in other.solver.assertions():
            self.solver.add(a)
        assert self.solver.check() == z3.sat
        other.solver.reset()
        other.solver = self.solver


def resolve_boolean_question(solver, exp):
    if not isinstance(exp, z3.BoolRef):
        exp = (exp != 0)

    if random.randint(0, 1):
        solver.push()
        solver.add(exp)
        result = solver.check() == z3.sat
        solver.pop()
    else:
        solver.push()
        solver.add(z3.Not(exp))
        result = solver.check() != z3.sat
        solver.pop()
    if result:
        solver.add(exp)
    else:
        solver.add(z3.Not(exp))
    assert solver.check()
    return result


name_index = 0


class schroedinteger(object):
    __class__ = int

    def __init__(
        self, choices=None, *, expression=None, shared_solver=None
    ):
        self._known_value = None
        self.shared_solver = shared_solver or SharedSolver()
        global name_index
        name_index += 1
        self.name = z3.Int("V%d" % (name_index,))
        if expression is None:
            expression = self.name
        else:
            self.shared_solver.solver.add(self.name == expression)
        self.expression = expression

        if choices is not None:
            self.shared_solver.solver.add(z3.Or(*[
                self.expression == c for c in choices
            ]))

        self.__cached_bit_length = None

    def __repr__(self):
        if self._known_value is not None:
            return repr(self._known_value)
        else:
            n = 6
            pv = self.possible_values(n)
            if pv is None:
                return "Indeterminate: %r" % (
                    self.expression,
                )
            if len(pv) == 1:
                return repr(pv[0])
            if len(pv) == n:
                pv.append('...')
            return "Indeterminate: %r {%s}" % (
                self.expression,
                ', '.join(map(str, pv))
            )

    def __bool__(self):
        if self._known_value is not None:
            return bool(self._known_value)
        else:
            if resolve_boolean_question(self.solver, self.expression):
                return True
            else:
                self._known_value = 0
                return False

    def __int__(self):
        # We don't double bounds each time because if we did then the expected
        # value would be infinite! Instead we increase by a smaller exponent
        # so the expectation is more reasonable.
        ub = 1024
        while not (self < ub):
            ub = int((ub * 3) // 2)
        lb = -1024
        while not (lb <= self):
            lb = int((lb * 3) // 2)
        while lb + 1 < ub:
            assert lb <= self <= ub
            mid = (lb + ub) // 2
            if self < mid:
                ub = mid
            else:
                lb = mid
        self._known_value = lb
        return lb

    def bit_length(self):
        if self.__cached_bit_length is None:
            if self < 0:
                self.__cached_bit_length = (-self).bit_length()
            elif self == 0:
                self.__cached_bit_length = 0
            else:
                n = 64
                while self >= 2 ** n:
                    n += 1
                while self < 2 ** n:
                    n -= 1
                self.__cached_bit_length = n + 1
        return self.__cached_bit_length

    @property
    def solver(self):
        return self.shared_solver.solver

    def _val_or_exp(self):
        if self._known_value is not None:
            return self._known_value
        pv = self.possible_values(2) or ()
        if len(pv) == 1:
            self._known_value = pv[0]
            return self._known_value
        return self.expression

    def possible_values(self, n=10):
        self.solver.push()
        result = []
        while len(result) < n:
            if self.solver.check() != z3.sat:
                break
            v = self.solver.model()[self.name]
            if v is None:
                assert not result
                return None
            result.append(v)
            self.solver.add(self.name != result[-1])
        self.solver.pop()
        assert result
        return result


def binary_operator(operator):
    def accept(self, other):
        if self._known_value is not None:
            return operator(self._known_value, other)
        if isinstance(other, schroedinteger):
            self.shared_solver.merge(other.shared_solver)
            if other._known_value is not None:
                return operator(self, other._known_value)
            return schroedinteger(
                expression=operator(self.expression, other.expression),
                shared_solver=self.shared_solver,
            )
        return schroedinteger(
            expression=operator(self.expression, other),
            shared_solver=self.shared_solver,
        )
    return accept


schroedinteger.__add__ = binary_operator(operator.add)
schroedinteger.__sub__ = binary_operator(operator.sub)
schroedinteger.__mul__ = binary_operator(operator.mul)
schroedinteger.__floordiv__ = binary_operator(operator.floordiv)
schroedinteger.__mod__ = binary_operator(operator.mod)
schroedinteger.__divmod__ = binary_operator(divmod)
schroedinteger.__pow__ = binary_operator(operator)


def int_to_bv(intexp):
    return z3.Z3_mk_int2bv(intexp.ctx_ref(), intexp.as_ast(), 1)


def bitwise_operator(opeerator):
    def accept(self, other):
        self_expression = self._val_or_exp()
        if isinstance(other, schroedinteger):
            self.shared_solver.merge(other.shared_solver)
            other_expression = other._val_or_exp()
        else:
            other_expression = other
        
    return accept


schroedinteger.__lshift__ = binary_operator(operator.lshift)
schroedinteger.__rshift__ = binary_operator(operator.rshift)
schroedinteger.__and__ = binary_operator(operator.and_)
schroedinteger.__or__ = binary_operator(operator.or_)
schroedinteger.__xor__ = binary_operator(operator.xor)


def swop(f):
    return lambda x, y: f(y, x)


schroedinteger.__radd__ = binary_operator(operator.add)
schroedinteger.__rsub__ = binary_operator(swop(operator.sub))
schroedinteger.__rmul__ = binary_operator(operator.mul)
schroedinteger.__rfloordiv__ = binary_operator(swop(operator.floordiv))
schroedinteger.__rmod__ = binary_operator(swop(operator.mod))
schroedinteger.__rdivmod__ = binary_operator(swop(divmod))
schroedinteger.__rpow__ = binary_operator(operator.pow)
schroedinteger.__rlshift__ = binary_operator(swop(operator.lshift))
schroedinteger.__rrshift__ = binary_operator(swop(operator.rshift))
schroedinteger.__rand__ = binary_operator(operator.and_)
schroedinteger.__ror__ = binary_operator(operator.or_)
schroedinteger.__rxor__ = binary_operator(operator.xor)


def binary_comparison(comparison, self_value):
    def accept(self, other):
        if self is other:
            return self_value
        if (
            self._known_value is not None and
            isinstance(other, schroedinteger) and
            other._known_value is not None
        ):
            return comparison(self._known_value, other._known_value)
        else:
            if isinstance(other, schroedinteger):
                self.shared_solver.merge(other.shared_solver)
                exp = other._val_or_exp()
            else:
                exp = other
            return resolve_boolean_question(
                self.solver,
                comparison(self._val_or_exp(), exp))
    return accept


schroedinteger.__lt__ = binary_comparison(operator.lt, False)
schroedinteger.__ne__ = binary_comparison(operator.ne, False)
schroedinteger.__gt__ = binary_comparison(operator.gt, False)
schroedinteger.__le__ = binary_comparison(operator.le, True)
schroedinteger.__eq__ = binary_comparison(operator.eq, True)
schroedinteger.__ge__ = binary_comparison(operator.ge, True)


def compute_unary(operator):
    def accept(self):
        exp = self._val_or_exp()
        if isinstance(exp, int):
            return operator(exp)
        return schroedinteger(
            expression=operator(exp), shared_solver=self.shared_solver)
    return accept


schroedinteger.__neg__ = compute_unary(operator.neg)
schroedinteger.__pos__ = compute_unary(operator.pos)
schroedinteger.__abs__ = compute_unary(abs)
schroedinteger.__invert__ = compute_unary(operator.invert)
