import pytest
from micromagneticmodel.tests.test_damping import TestDamping
from oommfc.dynamics import Damping


class TestDamping(TestDamping):
    def test_script(self):
        for alpha in self.valid_args:
            with pytest.raises(NotImplementedError):
                damping = Damping(alpha)

                damping.script()
