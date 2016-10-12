import pytest
import oommfc as oc
import micromagneticmodel.tests as mmt


class TestSTT(mmt.TestSTT):
    def test_script(self):
        for arg in self.valid_args:
            u, beta = arg
            stt = oc.STT(u, beta)
            with pytest.raises(NotImplementedError):
                stt.script()
