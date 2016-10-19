import oommfc as oc


class TestOOMMF:
    def test_status(self):
        oommf = oc.OOMMF()

        status = oommf.status()
        assert isinstance(status, dict)

    def test_call_oommf(self):
        oommf = oc.OOMMF()

        oommf.call_oommf(argstr="+v", where=None)
        oommf.call_oommf(argstr="+v", where="host")
        oommf.call_oommf(argstr="+v", where="docker")
