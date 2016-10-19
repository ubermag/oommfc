import oommfc as oc


class TestOOMMF:
    def test_status(self):
        oommf = oc.OOMMF()

        status = oommf.status()
        assert isinstance(status, dict)
