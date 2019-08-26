import os
import pytest
import oommfc as oc


def test_example_bar():
    # can we create the object?
    b = oc.examples.bar()

    # can it do something?
    _ = b.m.average
    assert b.name == 'example-bar'


def test_example_macrospin():
    # can we create the object?
    m = oc.examples.macrospin()

    # can it do something?
    _ = m.m.average
    assert m.name == 'example-macrospin'
