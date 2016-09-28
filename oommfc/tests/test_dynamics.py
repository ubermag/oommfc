import pytest
import oommfc as oc
import micromagneticmodel.tests as mmt


class TestDynamics(mmt.TestDynamics):
    def test_script(self):
        dynamics = oc.Dynamics()
        for term in self.terms:
            dynamics += term

            with pytest.raises(NotImplementedError):
                dynamics.script()
