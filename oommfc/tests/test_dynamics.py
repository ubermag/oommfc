import pytest
from micromagneticmodel.tests.test_dynamics import TestDynamics
from oommfc.dynamics import Dynamics


class TestDynamics(TestDynamics):
    def test_script(self):
        dynamics = Dynamics()
        for term in self.terms:
            dynamics += term

            with pytest.raises(NotImplementedError):
                dynamics.script()
