import oommfc as oc


class TestOOMMF:
    def setup(self):
        self.oommf = oc.OOMMF()

    def test_installed(self):
        assert self.oommf.installed("git") is True
        assert self.oommf.installed("OOMMF") is False

    def test_environment_variable(self):
        assert self.oommf.environment_variable("OOMMFTCL") is True
        assert self.oommf.environment_variable("OOMMFTCL2") is False

    def test_test_oommf(self):
        assert self.oommf.test_oommf() is True

    def test_version(self):
        version = self.oommf.version()
        assert isinstance(version, str)
        assert "." in version
        assert version[0].isdigit()
        assert version[-1].isdigit()
