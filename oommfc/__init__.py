from .oommf import OOMMF
from .hamiltonian import Exchange, UniaxialAnisotropy, \
    Demag, Zeeman, Hamiltonian
from .dynamics import Precession, Damping, STT, Dynamics
from .drivers import Driver, MinDriver, TimeDriver, HysteresisDriver
from .mesh import Mesh
from .system import System
from .data import Data
from micromagneticmodel.consts import mu0, e, me, kB, h, g, \
    hbar, gamma, muB, gamma0

__version__ = "0.5.6.11"
oommf = OOMMF()


def test():
    """Runs all the tests"""
    oommf.status(raise_exception=True)  # pragma: no cover
    import pytest  # pragma: no cover
    args = ["-m", "not travis", "-v", "--pyargs",
            "oommfc"]  # pragma: no cover
    pytest.main(args)  # pragma: no cover


def test_not_oommf():
    """ Runs tests that do not need an OOMMF installation"""
    import pytest  # pragma: no cover
    args = ["-m", "not travis", "-m", "not oommf", "-v",
            "--pyargs", "oommfc"]  # pragma: no cover
    pytest.main(args)  # pragma: no cover


def test_oommf():
    """Runs all tests that require an OOMMF installation."""
    oommf.status(raise_exception=True)  # pragma: no cover
    import pytest  # pragma: no cover
    args = ["-m", "oommf and not travis", "-v",
            "--pyargs", "oommfc"]  # pragma: no cover
    pytest.main(args)  # pragma: no cover
