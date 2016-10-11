import oommfc as oc


class TestOOMMF:
    def setup(self):
        self.oommf = oc.OOMMF()

    def test_installed(self):
        assert self.oommf.installed() is True
        assert self.oommf.installed("oommf") is True
        assert self.oommf.installed("OOMMF") is False

    def test_environment_variable(self):
        assert self.oommf.environment_variable("OOMMFTCL") is True
        assert self.oommf.environment_variable("OOMMFTCL2") is False

    def test_test_oommf(self):
        assert self.oommf.test_oommf() is True

    def test_version(self):
        assert self.oommf.test_oommf() is True
