import pytest
import pkg_resources
import oommfc.oommf
import oommfc.scripts
from .delete import delete
from .compute import compute
from .drivers import MinDriver, TimeDriver
from .evolvers import CGEvolver, EulerEvolver, RungeKuttaEvolver, \
    SpinTEvolver, SpinXferEvolver


def test():
    return pytest.main(['-m', 'not travis and not docker',
                        '-v', '--pyargs', 'oommfc'])  # pragma: no cover


def test_docker():
    return pytest.main(['-m', 'docker', '-v',
                        '--pyargs', 'oommfc'])  # pragma: no cover


__version__ = pkg_resources.get_distribution(__name__).version
__dependencies__ = pkg_resources.require(__name__)
