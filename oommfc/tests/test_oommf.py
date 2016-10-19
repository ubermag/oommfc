import oommfc as oc


class TestOOMMF:
    def test_status(self):
        oommf = oc.OOMMF()

        status = oommf.status()
        assert isinstance(status, dict)

    def test_call_oommf(self):
        oommf = oc.OOMMF()

        oommf.call(argstr="+v", where=None)
        oommf.call(argstr="+v", where="host")
        oommf.call(argstr="+v", where="docker")

    def test_call_oommf_host(self):
        oommf = oc.OOMMF()

        oommf._call_host(argstr="+v")
