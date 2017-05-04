import os
import shutil
import pytest
import oommfc as oc
import discretisedfield as df
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


@pytest.mark.oommf
def test_relax_with_cubicanisotropy():
    name = "cubic_anisotropy"
    L = 100e-9
    d = 5e-9
    Ms = 8e6

    # Remove any previous simulation directories.
    if os.path.exists(name):
        shutil.rmtree(name)

    system = oc.System(name=name)
    system.hamiltonian = oc.CubicAnisotropy(K1=5e6,
                                            u1=(1, 0, 0),
                                            u2=(0, 1, 0))

    mesh = oc.Mesh(p1=(0, 0, 0), p2=(L, L, L), cell=(d, d, d))

    def m_init(pos):
        x, y, z = pos
        if x < 30e-9:
            return (0.7, 0.1, 0.3)
        elif x > 70e-9:
            return (0.1, 0.7, 0.3)
        else:
            return (0.3, 0.1, 0.7)

    system.m = df.Field(mesh, value=m_init, norm=Ms)

    md = oc.MinDriver()
    md.drive(system)

    comp_value = 0.99*Ms
    assert system.m((10e-9, 0, 0))[0] > comp_value
    assert system.m((50e-9, 0, 0))[2] > comp_value
    assert system.m((80e-9, 0, 0))[1] > comp_value

    shutil.rmtree(name)
