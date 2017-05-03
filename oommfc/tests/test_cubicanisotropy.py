import oommfc as oc
import micromagneticmodel.tests as mmt


class TestCubicAnisotropy(mmt.TestCubicAnisotropy):
    def test_script(self):
        for K1, u1, u2 in self.valid_args:
            anisotropy = oc.CubicAnisotropy(K1=K1, u1=u1, u2=u2)
            script = anisotropy._script

            assert script.count("\n") == 7
            assert script[0] == "#"
            assert script[-1] == "\n"
            lines = script.split("\n")
            assert len(lines) == 8
            assert lines[0] == "# CubicAnisotropy"
            assert lines[2] == "  K1 {}".format(K1)
            assert lines[3] == "  axis1 {{{} {} {}}}".format(*u1)
            assert lines[4] == "  axis2 {{{} {} {}}}".format(*u2)
            assert lines[5] == "}"
