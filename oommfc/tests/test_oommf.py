import oommfc as oc


class TestOOMMF:
    def test_installed(self):
        oommf = oc.OOMMF()

        assert oommf.installed() is True
        assert oommf.installed("oommf") is True
        assert oommf.installed("OOMMF") is False
