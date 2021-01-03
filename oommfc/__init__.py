"""Main package"""
import pytest
import pkg_resources
import oommfc.oommf
import oommfc.scripts
from .delete import delete
from .compute import compute
from .drivers import Driver, MinDriver, TimeDriver, HysteresisDriver
from .evolvers import CGEvolver, EulerEvolver, RungeKuttaEvolver, \
    SpinTEvolver, SpinXferEvolver

__version__ = pkg_resources.get_distribution(__name__).version


def test():
    """Run all package tests.

    Examples
    --------
    1. Run all tests.

    >>> import oommfc as md
    ...
    >>> # md.test()

    """
    return pytest.main(['-m', 'not travis and not docker',
                        '-v', '--pyargs', 'oommfc', '-l'])  # pragma: no cover


def test_docker():
    """Run only Docker tests.

    Examples
    --------
    1. Run only Docker tests.

    >>> import oommfc as md
    ...
    >>> # md.test_docker()

    """
    return pytest.main(['-m', 'docker', '-v',
                        '--pyargs', 'oommfc', '-l'])  # pragma: no cover
