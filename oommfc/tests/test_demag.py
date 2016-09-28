import oommfc as oc
import micromagneticmodel.tests as mmt


class TestDemag(mmt.TestDemag):
    def test_script(self):
        demag = oc.Demag()

        script = demag.script()
        assert script.count("\n") == 3
        assert script[0] == "#"
        assert script[-1] == "\n"

        lines = script.split("\n")
        assert len(lines) == 4
        assert lines[0] == "# Demag"
        assert lines[1] == "Specify Oxs_Demag {}"
