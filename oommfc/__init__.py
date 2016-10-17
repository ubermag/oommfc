from .oommf import OOMMF
from .hamiltonian import Exchange, UniaxialAnisotropy, \
    Demag, Zeeman, Hamiltonian
from .dynamics import Precession, Damping, STT, Dynamics
from .drivers import Driver, MinDriver, TimeDriver, HysteresisDriver
from .mesh import Mesh
from .system import System
from micromagneticmodel.consts import mu0, e, muB, kB


def test():
    """Runs all the tests"""
    import pytest  # pragma: no cover
    pytest.main(["-v", "--pyargs", "oommfc"])  # pragma: no cover


def test_non_oommf():
    """ Runs tests that do not need an OOMMF installation"""
    import pytest  # pragma: no cover
    pytest.main(["-m", "not oommf", "-v", "--pyargs", "oommfc"])  # pragma: no cover


def test_oommf():
    """Runs all tests that require an OOMMF installation."""
    import pytest  # pragma: no cover
    pytest.main(["-m", "oommf", "-v", "--pyargs", "oommfc"])  # pragma: no cover

    
