import os
import pytest
import oommfc as oc


def test_example_bar():
    # can we create the object?
    b = oc.examples.bar()

    # can it do something?
    _ = b.m.average
    assert b.name == 'example-bar'

    ham = repr(b.hamiltonian).lower()
    for interaction in ['exchange', 'demag']:
        assert interaction in ham

    dyn = repr(b.dynamics).lower()
    for dynamics in ['precession', 'damping']:
        assert dynamics in dyn


def test_example_macrospin():
    # can we create the object?
    m = oc.examples.macrospin()

    # can it do something?
    _ = m.m.average
    assert m.name == 'example-macrospin'

    ham = repr(m.hamiltonian).lower()
    assert 'zeeman' in ham

    dyn = repr(m.dynamics).lower()
    for dynamics in ['precession', 'damping']:
        assert dynamics in dyn
