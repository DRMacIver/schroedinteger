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

import random
from functools import wraps
import operator


class Observable(object):
    def __init__(self, choices):
        choices = tuple(sorted(frozenset(choices)))
        if not choices:
            raise ValueError(
                "An observable must always have at least one option")
        for x in choices:
            if type(x) != int:
                raise TypeError(
                    "Choices for an observable must be vanilla integers but "
                    "got %r of type %s" % (x, type(x).__name__)
                )
        self.choices = list(choices)
        self.change_counter = 0

    def __repr__(self):
        return "Observable(%r)" % (self.choices,)

    @property
    def is_determined(self):
        assert self.choices
        return len(self.choices) == 1


def resolve_observation(observables, function):
    observables = set(observables)
    if not observables:
        return function({})
    indeterminate = [o for o in observables if not o.is_determined]
    # This is arbitrary, and is only to avoid hash randomization affecting the
    # answer.
    indeterminate.sort(
        key=lambda o: o.choices
    )

    if len(indeterminate) == 0:
        assignment = {}
        for o in observables:
            assignment[o] = o.choices[0]
        return function(assignment)

    if len(indeterminate) == 1:
        decider = indeterminate[0]
        assignment = {}
        for o in observables:
            assignment[o] = o.choices[0]
        results = {}
        for v in decider.choices:
            assignment[decider] = v
            results.setdefault(function(assignment), []).append(v)
        results = sorted(results.items())
        if len(results) == 1:
            return results[0][0]
        else:
            answer, resolution = random.choice(results)
            decider.choices = list(resolution)
            decider.change_counter += 1
            return answer

    # Now the order actually matters, so we shuffle to deliberately remove any
    # biasing.
    random.shuffle(indeterminate)

    if len(indeterminate) == 2:
        x, y = indeterminate

        assignment = {}
        for o in observables:
            assignment[o] = o.choices[0]

        results = {}
        for u in x.choices:
            for v in y.choices:
                assignment[x] = u
                assignment[y] = v
                results.setdefault(function(assignment), set()).add((u, v))
        results = sorted(results.items())
        assert results
        if len(results) == 1:
            return results[0][0]
        else:
            answer, resolution = random.choice(results)
            resolution = sorted(set(resolution))
            a, b = random.choice(resolution)
            x.choices = [
                u for u in x.choices if (u, b) in resolution
            ]
            assert a in x.choices
            y.choices = [
                v for v in y.choices if all(
                    (u, v) in resolution for u in x.choices
                )
            ]
            x.change_counter += 1
            y.change_counter += 1
            assert b in y.choices
            return answer

    # We don't want to deal with too much indeterminacy so we resolve a
    # random subset of the variables to get us down to two.
    while len(indeterminate) > 2:
        r = indeterminate.pop()
        r.choices = (random.choice(r.choices),)
        r.change_counter += 1

    assert len([o for o in observables if not o.is_determined]) <= 2
    # We're now down to two so can try again.
    return resolve_observation(observables, function)


def cache_answer(fn):
    cache_key = '_%s_cache_key' % (fn.__name__,)

    @wraps(fn)
    def accept(self):
        try:
            return getattr(self, cache_key)
        except AttributeError:
            pass
        if self.is_determined:
            result = getattr(self.determined_value, fn.__name__)()
        else:
            result = fn(self)
        setattr(self, cache_key, result)
        return result
    return accept


def possible_values(observables, function):
    indeterminate = [o for o in observables if not o.is_determined]
    indeterminate.sort(
        key=lambda o: o.choices
    )
    if not indeterminate:
        return True, {resolve_observation(observables, function)}

    if len(indeterminate) == 1:
        determiner = indeterminate[0]
        assignment = {}
        for o in observables:
            assignment[o] = o.choices[0]
        result = set()
        for o in determiner.choices:
            assignment[determiner] = o
            result.add(function(assignment))
        return True, result
    if len(indeterminate) == 2:
        if len(indeterminate[0].choices) * len(indeterminate[1].choices) <= 10:
            result = set()
            assignment = {}
            for o in observables:
                assignment[o] = random.choice(o.choices)
            x, y = indeterminate
            for u in x.choices:
                assignment[x] = u
                for v in y.choices:
                    assignment[y] = v
                    result.add(function(assignment))
            return True, result
    result = set()
    for _ in range(10):
        assignment = {}
        for o in observables:
            assignment[o] = random.choice(o.choices)
        result.add(function(assignment))
    return False, result


class schroedinteger(object):
    __class__ = int

    def __init__(
        self, choices=None, *, observables=None, observe_value=None
    ):
        if (observables is None) != (observe_value is None):
            raise ValueError(
                "observables and observe_value must be set together"
            )
        if observables is None and choices is None:
            raise ValueError("must specify either choices or a calculation")
        if choices is not None:
            if observables is not None or observe_value is not None:
                raise ValueError(
                    "If choices is a non-None value then observables and "
                    "observe_value cannot be specified additionally."
                )
            observable = Observable(choices)
            observables = {observable}
            observe_value = lambda assignment: assignment[observable]

        self.observables = observables
        self._observe_value = observe_value
        self.__cached_determined = False
        self.__cached_value = None
        self.repr_cache_marker = None

    def observe_value(self, resolution):
        if self.is_determined:
            return self.determined_value
        else:
            return self._observe_value(resolution)

    def __repr__(self):
        cache_marker = {
            o: o.change_counter for o in self.observables
        }
        if cache_marker == self.repr_cache_marker:
            return self.repr_cache

        complete, options = possible_values(
            self.observables, self.observe_value
        )
        options = list(options)
        options.sort()
        if complete:
            if len(options) == 1:
                result = repr(list(options)[0])
            else:
                result = "indeterminate: {%s}" % (
                    ', '.join(map(str, options)),)
        else:
            random.shuffle(options)
            result = "indeterminate: {%s, ...}" % (
                ', '.join(map(str, options)),)
        self.repr_cache = result
        self.repr_cache_marker = cache_marker
        return result

    @cache_answer
    def __bool__(self):
        return bool(
            resolve_observation(
                self.observables,
                lambda resolution: bool(self.observe_value(resolution))))

    @cache_answer
    def __int__(self):
        return resolve_observation(self.observables, self.observe_value)

    def __hash__(self):
        return hash(int(self))

    __index__ = __int__

    def __float__(self):
        return float(int(self))

    def __complex__(self):
        return complex(int(self))

    def __truediv__(self, other):
        return int(self) / int(other)

    def __rtruediv__(self, other):
        return int(other) / int(self)

    @property
    def is_determined(self):
        if self.__cached_determined:
            return True
        self.__cached_determined = all(
            o.is_determined for o in self.observables
        )
        return self.__cached_determined

    @property
    def determined_value(self):
        if self.__cached_value is not None:
            return self.__cached_value
        if not self.is_determined:
            raise ValueError("Value has not yet been determined")
        self.__cached_value = resolve_observation(
            self.observables, self._observe_value
        )
        assert isinstance(self.__cached_value, int)
        return self.__cached_value


def resolve_binary(operator, self, other):
    assert isinstance(self, schroedinteger)
    if self.is_determined:
        return operator(self.determined_value, other)
    if isinstance(other, schroedinteger):
        if other.is_determined:
            return resolve_binary(operator, self, other.determined_value)
        obvs = self.observables | other.observables
        return schroedinteger(
            observables=obvs,
            observe_value=lambda resolution: operator(
                self.observe_value(resolution),
                other.observe_value(resolution),
            ))
    else:
        return schroedinteger(
            observables=self.observables,
            observe_value=lambda resolution: operator(
                self.observe_value(resolution), other))


def observe_comparison(comparison, value_on_self):
    def accept(self, other):
        if self is other:
            return value_on_self
        return bool(resolve_binary(comparison, self, other))
    return accept


schroedinteger.__lt__ = observe_comparison(operator.lt, False)
schroedinteger.__ne__ = observe_comparison(operator.ne, False)
schroedinteger.__gt__ = observe_comparison(operator.gt, False)
schroedinteger.__le__ = observe_comparison(operator.le, True)
schroedinteger.__eq__ = observe_comparison(operator.eq, True)
schroedinteger.__ge__ = observe_comparison(operator.ge, True)


def compute_arithmetic(operator, value_on_zero=None):
    def accept(self, other):
        if self.is_determined:
            return operator(self.determined_value, other)
        if isinstance(other, schroedinteger):
            return resolve_binary(operator, self, other)
        if value_on_zero is not None and other == 0:
            return value_on_zero(self)
        else:
            return schroedinteger(
                observables=self.observables,
                observe_value=lambda resolution: operator(
                    self.observe_value(resolution), other))
    return accept

schroedinteger.__add__ = compute_arithmetic(operator.add, lambda self: self)
schroedinteger.__sub__ = compute_arithmetic(operator.sub, lambda self: self)
schroedinteger.__mul__ = compute_arithmetic(operator.mul, lambda self: 0)
schroedinteger.__floordiv__ = compute_arithmetic(operator.floordiv)
schroedinteger.__mod__ = compute_arithmetic(operator.mod)
schroedinteger.__divmod__ = compute_arithmetic(divmod)
schroedinteger.__pow__ = compute_arithmetic(operator.__pow__, lambda self: 1)
schroedinteger.__lshift__ = compute_arithmetic(
    operator.lshift, lambda self: self)
schroedinteger.__rshift__ = compute_arithmetic(
    operator.rshift, lambda self: self)
schroedinteger.__and__ = compute_arithmetic(operator.and_, lambda self: 0)
schroedinteger.__or__ = compute_arithmetic(operator.or_, lambda self: self)
schroedinteger.__xor__ = compute_arithmetic(operator.xor, lambda self: self)


def swop(f):
    return lambda x, y: f(y, x)


schroedinteger.__radd__ = compute_arithmetic(operator.add, lambda self: self)
schroedinteger.__rsub__ = compute_arithmetic(
    swop(operator.sub), lambda self: -self)
schroedinteger.__rmul__ = compute_arithmetic(operator.mul, lambda self: 0)
schroedinteger.__rfloordiv__ = compute_arithmetic(swop(operator.floordiv))
schroedinteger.__rmod__ = compute_arithmetic(swop(operator.mod))
schroedinteger.__rdivmod__ = compute_arithmetic(swop(divmod))
schroedinteger.__rpow__ = compute_arithmetic(
    swop(operator.__pow__), lambda self: 0 if self else 1)
schroedinteger.__rlshift__ = compute_arithmetic(
    swop(operator.lshift), lambda self: 0)
schroedinteger.__rrshift__ = compute_arithmetic(
    swop(operator.rshift), lambda self: 0)
schroedinteger.__rand__ = compute_arithmetic(operator.and_, lambda self: 0)
schroedinteger.__ror__ = compute_arithmetic(operator.or_, lambda self: self)
schroedinteger.__rxor__ = compute_arithmetic(operator.xor, lambda self: self)


def compute_unary(operator):
    def accept(self):
        if self.is_determined:
            return operator(self.determined_value)
        else:
            return schroedinteger(
                observables=self.observables,
                observe_value=lambda resolution: operator(
                    self.observe_value(resolution)))
    return accept


schroedinteger.__neg__ = compute_unary(operator.neg)
schroedinteger.__pos__ = compute_unary(operator.pos)
schroedinteger.__abs__ = compute_unary(abs)
schroedinteger.__invert__ = compute_unary(operator.invert)
