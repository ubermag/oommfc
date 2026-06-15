from pathlib import Path

import pytest
from ubermagtable.tests.test_table import *  # noqa: F403

from oommfc.plugins import table_from_file


def samples():
    return Path(__file__).parent / "test_sample" / "tables"


energy_minimisation_samples = [
    "oommf-issue1.odt",
    "oommf-mel-file.odt",
    "oommf-minsteps.odt",
    "oommf-new-file1.odt",
    "oommf-new-file3.odt",
    "oommf-new-file4.odt",
    "oommf-old-file3.odt",
    "oommf-old-file7.odt",
]

llg_samples = [
    "oommf-new-file2.odt",
    "oommf-new-file5.odt",
    "oommf-old-file1.odt",
    "oommf-old-file2.odt",
    "oommf-old-file4.odt",
    "oommf-old-file5.odt",
    "oommf-old-file6.odt",
    "oommf-old-file8.odt",
]


@pytest.fixture(scope="session", params=llg_samples)
def table_llg_factory(request):
    """LLG tables."""

    def _inner(**kwargs):
        return table_from_file(samples() / request.param, **kwargs)

    return _inner


@pytest.fixture(scope="session", params=energy_minimisation_samples)
def table_minimisation_factory(request):
    def _inner(**kwargs):
        return table_from_file(samples() / request.param, **kwargs)

    return _inner


@pytest.fixture(scope="session")
def table_hysteresis_factory():
    def _inner(**kwargs):
        return table_from_file(samples() / "oommf-hysteresis1.odt", **kwargs)

    return _inner


@pytest.fixture(
    scope="session",
    params=energy_minimisation_samples + llg_samples + ["oommf-hysteresis1.odt"],
)
def table_factory(request):
    """Energy minimisation or LLG tables."""

    def _inner(**kwargs):
        return table_from_file(samples() / request.param, **kwargs)

    return _inner


@pytest.fixture(scope="session")
def table_llg_25ps():
    """LLG data with tmax=25ps."""
    return table_from_file(samples() / "oommf-old-file1.odt", x="t")
