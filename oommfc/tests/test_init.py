import oommfc as oc


def test_version():
    assert isinstance(oc.__version__, str)
    assert '.' in oc.__version__
