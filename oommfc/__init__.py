"""OOMMF calculator."""
import pytest
import pkg_resources
import oommfc.oommf
import oommfc.scripts
from .delete import delete
from .compute import compute
from .drivers import Driver, MinDriver, TimeDriver, HysteresisDriver
from .evolvers import (CGEvolver, EulerEvolver, RungeKuttaEvolver,
                       SpinTEvolver, SpinXferEvolver, UHH_ThetaEvolver,
                       Xf_ThermHeunEvolver, Xf_ThermSpinXferEvolver)

__version__ = pkg_resources.get_distribution(__name__).version

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
