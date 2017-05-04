import oommfc as oc
import micromagneticmodel.tests as mmt


class TestUniaxialAnisotropy(mmt.TestUniaxialAnisotropy):
    def test_script(self):
        for K1, K2, u in self.valid_args:
            anisotropy = oc.UniaxialAnisotropy(K1=K1, K2=K2, u=u)
            script = anisotropy._script

            assert script[0] == "#"
            assert script[-1] == "\n"
            lines = script.split("\n")
            assert lines[0] == "# UniaxialAnisotropy"
            assert lines[2] == "  K1 {}".format(K1)
            assert lines[-4] == "  axis {{{} {} {}}}".format(*u)
            assert lines[-3] == "}"

            if K2 == 0:
                assert script.count("\n") == 6
                assert len(lines) == 7
                assert lines[1] == "Specify Oxs_UniaxialAnisotropy {"
            else:
                assert script.count("\n") == 7
                assert len(lines) == 8
                assert lines[1] == "Specify Southampton_UniaxialAnisotropy4 {"
                assert lines[3] == "  K2 {}".format(K2)
