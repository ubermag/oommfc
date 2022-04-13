import pytest

import oommfc as oc


@pytest.fixture(scope="module")
def calculator():
    return oc
