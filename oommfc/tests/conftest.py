import pytest

import oommfc as oc

not_supported_by_oommf = ["test_relax_check_for_energy", "test_relaxdriver"]


def pytest_collection_modifyitems(items):
    """Mark known failures of tests provided by ``ubermagtable.testing``."""
    for item in items:
        if item.path.name == "test_table.py" and item.name.startswith(
            "test_table_columns[oommf-issue1.odt-"
        ):
            item.add_marker(
                pytest.mark.xfail(
                    reason="Column names collide once the OOMMF class prefixes "
                    "Oxs_ and My_ are stripped.",
                    strict=True,
                )
            )


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
