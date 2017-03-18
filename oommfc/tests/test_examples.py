import oommfc as oc


def test_example_bar():
    # can we create the object?
    b = oc.examples.bar()

    # can it do something?
    b.m.average
    assert b.name == 'example-bar'

    ham = repr(b.hamiltonian).lower()
    for interaction in ['exchange', 'demag']:
        assert interaction in ham

    dyn = repr(b.dynamics).lower()
    for dynamics in ['precession', 'damping']:
        assert dynamics in dyn
