import oommfc as oc
import micromagneticmodel.tests as mmt


class TestZeeman(mmt.TestZeeman):
    def test_script(self):
        for H in self.valid_args:
            zeeman = oc.Zeeman(H=H)

            script = zeeman._script
            assert script.count("\n") == 10
            assert script[0] == "#"
            assert script[-1] == "\n"

            lines = script.split("\n")
            assert len(lines) == 11
            assert lines[0] == "# FixedZeeman"
            assert lines[1] == "Specify Oxs_FixedZeeman {"
            assert lines[2] == "  field {"
            assert lines[3] == "    Oxs_UniformVectorField {"
            assert lines[4] == "      vector {{{} {} {}}}".format(*H)
            assert lines[5] == "    }"
            assert lines[6] == "  }"
            assert lines[7] == "  multiplier 1"
            assert lines[8] == "}"
