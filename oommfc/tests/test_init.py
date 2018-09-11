import oommfc as oc

def test_version():
    assert isinstance(oc.__version__, str)
    assert '.' in oc.__version__

def test_dependencies():
    assert isinstance(oc.__dependencies__, list)
    assert len(oc.__dependencies__) > 0
    
