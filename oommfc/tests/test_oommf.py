import pytest
import oommfc as oc


class TestOOMMF:
    def setup(self):
        self.oommf = oc.OOMMF()

    def test_installed(self):
        assert self.oommf.installed("ls") is True
        assert self.oommf.installed("OOMMF") is False

    def test_oommf_path(self):
        assert isinstance(self.oommf.oommf_path("OOMMFTCL"), str)
        with pytest.raises(Exception):
            assert self.oommf.oommf_path("OOMMFTCL2")

    def test_test_oommf(self):
        self.oommf.test_oommf()
        assert self.oommf.host is True
        assert self.oommf.docker is False
