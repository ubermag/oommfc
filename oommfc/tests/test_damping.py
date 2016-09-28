import pytest
import oommfc as oc
import micromagneticmodel.tests as mmt


class TestDamping(mmt.TestDamping):
    def test_script(self):
        for alpha in self.valid_args:
            damping = oc.Damping(alpha)
            with pytest.raises(NotImplementedError):
                damping.script()
