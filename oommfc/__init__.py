import os
import time
import pytest
import pkg_resources
import oommfc.oommf
from .hamiltonian import Exchange, UniaxialAnisotropy, \
    Demag, Zeeman, DMI, CubicAnisotropy, Hamiltonian
from .dynamics import Precession, Damping, STT, Dynamics
from .drivers import Driver, MinDriver, TimeDriver, HysteresisDriver
from .mesh import Mesh
from .system import System
from .data import Data
from micromagneticmodel.consts import mu0, e, me, kB, h, g, \
    hbar, gamma, muB, gamma0
from . import examples


__version__ = pkg_resources.get_distribution(__name__).version
__dependencies__ = pkg_resources.require(__name__)


def _run_tests(tag):
    args = ['-m', tag, '-v', '--pyargs', 'oommfc']  # pragma: no cover
    return pytest.main(args)  # pragma: no cover


def test():
    return(_run_tests('not travis and not docker'))  # pragma: no cover


def test_not_oommf():
    return(_run_tests('not oommf and not travis'))  # pragma: no cover


def test_oommf():
    return(_run_tests('oommf and not travis '
                      'and not docker'))  # pragma: no cover


def test_docker():
    return(_run_tests('docker'))  # pragma: no cover
