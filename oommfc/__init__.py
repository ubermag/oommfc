from .oommf import get_oommf_runner
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


def test():
    """Runs all the tests"""
    get_oommf_runner()  # pragma: no cover
    import pytest  # pragma: no cover
    args = ["-m", "not travis", "-v", "--pyargs",
            "oommfc"]  # pragma: no cover
    return pytest.main(args)  # pragma: no cover


def test_not_oommf():
    """ Runs tests that do not need an OOMMF installation"""
    import pytest  # pragma: no cover
    args = ["-m", "not travis", "-m", "not oommf", "-v",
            "--pyargs", "oommfc"]  # pragma: no cover
    return pytest.main(args)  # pragma: no cover


def test_oommf():
    """Runs all tests that require an OOMMF installation."""
    get_oommf_runner()  # pragma: no cover
    import pytest  # pragma: no cover
    args = ["-m", "oommf and not travis", "-v",
            "--pyargs", "oommfc"]  # pragma: no cover
    return pytest.main(args)  # pragma: no cover


def test_oommf_overhead(t=1e-12):
    """Run a macrospin example for time t, return system object.

    returns (time, mifpath) with
      - time : real time it took to call oommf (via Timedriver)
      - mifpath : the path to the mif file used (so that this can be re-used)

    Additional information will be printed.

    This can be used to measure/test the performance overhead of calling OOMMF.
    """
    import os
    import time

    system = examples.macrospin()

    td = TimeDriver()
    start = time.time()
    td.drive(system, t=0.001e-9, n=1)
    stop = time.time()
    time_ = stop - start
    print("Duration of calling OOMMF through oommfc: {:.4}s".format(time_))
    print("oommfc.oommf.get_oommf_runner(): {}".format(get_oommf_runner()))
    mifpath = os.path.realpath('example-macrospin/example-macrospin.mif')
    return time_, mifpath
