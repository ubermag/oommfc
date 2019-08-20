import pytest
import oommfc as oc
import micromagneticmodel.tests as mmt


class TestZhangLi:
    def test_script(self):
        zhangli = oc.ZhangLi(u=1e5, beta=0.5)
        with pytest.raises(NotImplementedError):
            zhangli._script()
