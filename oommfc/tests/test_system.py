import discretisedfield as df
import oommfc as oc


class TestSystem:
    def test_script(self):
        system = oc.System(name="test_system")

        system.hamiltonian += oc.Exchange(1e-12)
        system.hamiltonian += oc.Demag()
        system.hamiltonian += oc.UniaxialAnisotropy(1e3, (0, 1, 0))
        system.hamiltonian += oc.Zeeman((0, 1e6, 0))

        system.dynamics += oc.Precession(2.211e5)
        system.dynamics += oc.Damping(0.1)

        mesh = oc.Mesh((0, 0, 0), (5, 5, 5), (1, 1, 1))

        system.m = df.Field(mesh, dim=3, value=(0, 1, 0), norm=1)

        script = system._script

        assert script[0] == "#"
        assert script[-1] == "\n"
        assert script.count("#") == 6
        assert script.count("Specify") == 6
        assert "Exchange" in script
        assert "Demag" in script
        assert "Zeeman" in script
        assert "UniaxialAnisotropy" in script
        assert "BoxAtlas" in script
        assert "RectangularMesh" in script
