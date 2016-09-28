import pytest
import oommfc as oc
import micromagneticmodel.tests as mmt


class TestPrecession(mmt.TestPrecession):
    def test_script(self):
        for gamma in self.valid_args:
            precession = oc.Precession(gamma)
            with pytest.raises(NotImplementedError):
                precession.script()
