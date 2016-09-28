import oommfc as oc
import micromagneticmodel.tests as mmt


class TestZeeman(mmt.TestZeeman):
    def test_script(self):
        for H in self.valid_args:
            name = 'zeeman_test'
            zeeman = oc.Zeeman(H, name=name)

            script = zeeman.script()
            assert script.count("\n") == 10
            assert script[0] == "#"
            assert script[-1] == "\n"

            lines = script.split("\n")
            assert len(lines) == 11
            assert lines[0] == "# FixedZeeman"
            assert lines[1] == "Specify Oxs_FixedZeeman:{} {{".format(name)
            assert lines[2] == "  field {"
            assert lines[3] == "    Oxs_UniformVectorField {"
            assert lines[4] == "      vector {{{} {} {}}}".format(H[0],
                                                                  H[1],
                                                                  H[2])
            assert lines[5] == "    }"
            assert lines[6] == "  }"
            assert lines[7] == "  multiplier 1"
            assert lines[8] == "}"
