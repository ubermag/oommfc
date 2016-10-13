from .oommf import OOMMF
from .hamiltonian import Exchange, UniaxialAnisotropy, \
    Demag, Zeeman, Hamiltonian
from .dynamics import Precession, Damping, STT, Dynamics
from .drivers import Driver, MinDriver, TimeDriver, HysteresisDriver
from .mesh import Mesh
from .system import System
from micromagneticmodel.consts import mu0


def test():
    import pytest  # pragma: no cover
    pytest.main(["--pyargs", "oommfc"])  # pragma: no cover
