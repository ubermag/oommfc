import pytest

import oommfc as oc

not_supported_by_oommf = ["test_relax_check_for_energy", "test_relaxdriver"]


@pytest.fixture(scope="module")
def calculator():
    return oc


@pytest.fixture(autouse=True)
def skip_unsupported_or_missing(request):
    requesting_test_function = (
        f"{request.cls.__name__}.{request.function.__name__}"
        if request.cls
        else request.function.__name__
    )
    if requesting_test_function in not_supported_by_oommf:
        pytest.skip("Not supported by OOMMF.")
