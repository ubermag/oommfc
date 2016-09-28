import oommfc as oc
import micromagneticmodel.tests as mmt


class TestUniaxialAnisotropy(mmt.TestUniaxialAnisotropy):
    def test_script(self):
        for arg in self.valid_args:
            K = arg[0]
            u = arg[1]
            name = "anisotropy_test"

            anisotropy = oc.UniaxialAnisotropy(K, u, name=name)

            script = anisotropy.script()
            assert script.count("\n") == 6
            assert script[0] == "#"
            assert script[-1] == "\n"

            lines = script.split("\n")
            assert len(lines) == 7
            assert lines[0] == "# UniaxialAnisotropy"
            assert lines[1] == "Specify Oxs_UniaxialAnisotropy {"
            assert lines[2] == "  K1 {}".format(K)
            assert lines[3] == "  axis {{{} {} {}}}".format(u[0], u[1], u[2])
            assert lines[4] == "}"
