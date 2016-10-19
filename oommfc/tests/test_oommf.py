import oommfc as oc


class TestOOMMF:
    def test_status(self):
        status = oc.oommf.status()
        assert isinstance(status, dict)

    def test_call_oommf(self):
        oc.oommf.call(argstr="+v", where=None)
        oc.oommf.call(argstr="+v", where="host")
        oc.oommf.call(argstr="+v", where="docker")

    def test_call_oommf_host(self):
        oc.oommf.call_host(argstr="+v")
