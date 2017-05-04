import os
import pytest
import oommfc as oc


@pytest.mark.oommf
def test_test_oommf_overhead():
    # can we create the object?
    time_, mifpath = oc.test_oommf_overhead()

    assert isinstance(time_, float)
    assert isinstance(mifpath, str)
    assert os.path.exists(mifpath)
