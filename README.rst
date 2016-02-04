Schroedinteger
==============

This module is a terrible hack, but it's kinda cool that it works. This is the
attitude you should enter in with.

It's not really production ready. It's passably tested, and it seems to work,
but I make no real claims beyond that. If you use it you will almost certainly
run into problems.

The concept here is as follows: Suppose we want to test something by throwing
random data at it, e.g. using `Hypothesis <http://hypothesis.readthedocs.org>`_,
but the subset of the data we do anything useful with is extremely finicky
and we don't have a good handle on what a useful distribution would be.

But if we define our own type, we have control over the comparison operators.
Can we then use that to look at the questions the code asks about our data
determine the data we feed in based on the answers we want to give?

A schroedinteger answers that question affirmatively. Every other question it
holds off judgement on for as long as possible.

A schroedinteger behaves in as many ways as possible as if it were a real
integer. However it's very indecisive and hasn't necessarily decided *which*
integer it is.

You create it in a superposition of values. After that, every time you ask a
question about its value, it determines a range of possible answers, picks one
at random, and updates its knowledge about the range of values it could
possibly have:

.. code:: pycon

    >>> from schroedinteger import schroedinteger
    >>> x = schroedinteger([1, 2, 3, 4, 5, 6, 7])
    >>> x
    indeterminate: {1, 2, 3, 4, 5, 6, 7}
    >>> x >= 4
    False
    >>> x
    indeterminate: {1, 2, 3}
    >>> x == 1
    False
    >>> x
    indeterminate: {2, 3}
    >>> x == 2
    True
    >>> x
    2

When two schroedintegers interact they may force some observations about
each other:


.. code:: pycon

    >>> x = schroedinteger(range(10))
    >>> y = schroedinteger(range(5, 15))
    >>> x < y
    False
    >>> x
    indeterminate: {8, 9}
    >>> y
    indeterminate: {5, 6, 7, 8}


In general, schroedintegers try to force as little information as possible but
there are a number of simplifications made behind the scenes to keep things
tractable.

For example, a much wider range of possible values for x and y would have been
possible here, but the library wants to keep x and y independent: After that
interaction, the value of x and y shouldn't affect each other further.

You can perform normal arithmetic on schroedintegers:

.. code:: pycon

    >>> x = schroedinteger({1, 3, 7})
    >>> y = schroedinteger({-1, 1})
    >>> x * y
    indeterminate: {-7, -3, -1, 1, 3, 7}

When you create values like this, their eventual values are forced to remain
consistent, so you should never see things in an inconsistent state:


.. code:: pycon

    >>> x = schroedinteger({1, 3, 7})
    >>> y = schroedinteger({-1, 1})
    >>> z = x * y
    >>> z
    indeterminate: {-7, -3, -1, 1, 3, 7}
    >>> x == 1
    False
    >>> x == 3
    False
    >>> z
    indeterminate: {-7, 7}
    >>> z == -7
    True
    >>> z
    -7
    >>> y
    -1

In general the observed behaviour of any program using schroedintegers should
always be identical to a program where it turned out they were specific values
all along and the tester was just really good at guessing the right values.
