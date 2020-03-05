import pytest
import pkg_resources
import oommfc.oommf
import oommfc.script
from .drivers import MinDriver, TimeDriver
from .evolvers import CGEvolver, EulerEvolver, RungeKuttaEvolver, \
    SpinTEvolver
from . import examples


__version__ = pkg_resources.get_distribution(__name__).version
__dependencies__ = pkg_resources.require(__name__)


def _run_tests(tag):
    args = ['-m', tag, '-v', '--pyargs', 'oommfc']  # pragma: no cover
    return pytest.main(args)  # pragma: no cover


def test():
    return(_run_tests('not travis and not docker'))  # pragma: no cover


def test_docker():
    return(_run_tests('docker'))  # pragma: no cover
