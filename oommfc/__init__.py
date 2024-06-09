"""OOMMF calculator."""

import importlib.metadata

import pytest

import oommfc.oommf
import oommfc.scripts
from .compute import compute as compute
from .delete import delete as delete
from .drivers import Driver as Driver
from .drivers import HysteresisDriver as HysteresisDriver
from .drivers import MinDriver as MinDriver
from .drivers import TimeDriver as TimeDriver
from .evolvers import CGEvolver as CGEvolver
from .evolvers import EulerEvolver as EulerEvolver
from .evolvers import RungeKuttaEvolver as RungeKuttaEvolver
from .evolvers import SpinTEvolver as SpinTEvolver
from .evolvers import SpinXferEvolver as SpinXferEvolver
from .evolvers import UHH_ThetaEvolver as UHH_ThetaEvolver
from .evolvers import Xf_ThermHeunEvolver as Xf_ThermHeunEvolver
from .evolvers import Xf_ThermSpinXferEvolver as Xf_ThermSpinXferEvolver

__version__ = importlib.metadata.version(__package__)

runner = oommfc.oommf.oommf.Runner()
"""Controls the default runner.

``runner`` gives access to the default runner OOMMF used by ``oommfc``. For
details refer to ``oommfc.runner.Runner``.

Examples
--------
``runner.runner``
    Returns the default runner; selects the best available runner if unset. A
    different ``OOMMFRunner`` can be passed to be used instead. The new runner
    is tested first.

``runner.autoselect_runner()``
    Lets ``oommfc`` select the best runner. Can be used to reset the runner
    after overwriting it manually.

See Also
--------
:py:class:`~oommfc.oommf.Runner`

"""


def test():
    """Run all package tests.

    Examples
    --------
    1. Run all tests.

    >>> import oommfc as md
    ...
    >>> # md.test()

    """
    return pytest.main(
        ["-m", "not travis and not docker", "-v", "--pyargs", "oommfc", "-l"]
    )  # pragma: no cover


def test_docker():
    """Run only Docker tests.

    Examples
    --------
    1. Run only Docker tests.

    >>> import oommfc as md
    ...
    >>> # md.test_docker()

    """
    return pytest.main(
        ["-m", "docker", "-v", "--pyargs", "oommfc", "-l"]
    )  # pragma: no cover
