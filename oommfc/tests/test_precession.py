import pytest
from micromagneticmodel.tests.test_precession import TestPrecession
from oommfc.dynamics import Precession


class TestPrecession(TestPrecession):
    def test_script(self):
        for gamma in self.valid_args:
            with pytest.raises(NotImplementedError):
                precession = Precession(gamma)

                precession.script()
