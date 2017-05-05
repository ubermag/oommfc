import os
import pytest
import oommfc as oc


def test_example_bar():
    # can we create the object?
    b = oc.examples.bar()

    # can it do something?
    _ = b.m.average
    assert b.name == 'example-bar'

    for interaction in ['exchange', 'demag']:
        assert interaction in repr(b.hamiltonian).lower()

    for dynamics in ['precession', 'damping']:
        assert dynamics in repr(b.dynamics).lower()


def test_example_macrospin():
    # can we create the object?
    m = oc.examples.macrospin()

    # can it do something?
    _ = m.m.average
    assert m.name == 'example-macrospin'

    assert 'zeeman' in repr(m.hamiltonian).lower()

    for dynamics in ['precession', 'damping']:
        assert dynamics in repr(m.dynamics).lower()
