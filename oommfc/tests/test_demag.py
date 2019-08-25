import os
import shutil
import oommfc as oc
import discretisedfield as df


class TestDemag:
    def test_script(self):
        demag = oc.Demag()
        assert 'asymptotic_radius' not in demag._script

        demag = oc.Demag(asymptotic_radius=5)
        assert 'asymptotic_radius' in demag._script

    def test_demag(self):
        p1 = (-10e-9, 0, 0)
        p2 = (10e-9, 1e-9, 1e-9)
        cell = (1e-9, 1e-9, 1e-9)
        mesh = oc.Mesh(p1=p1, p2=p2, cell=cell)

        name = 'demag'
        if os.path.exists(name):
            shutil.rmtree(name)

        Ms = 1e6

        def norm_fun(pos):
            x, y, z = pos
            if -9e-9 <= x <= 9e-9:
                return 0
            else:
                return Ms

        system = oc.System(name=name)
        system.hamiltonian = oc.Demag()
        system.m = df.Field(mesh, dim=3, value=(0, 0, 1), norm=norm_fun)

        md = oc.MinDriver()
        md.drive(system)

        value = system.m((-9.5e-9, 0.5e-9, 0.5e-9))
        value = system.m((9.5e-9, 0.5e-9, 0.5e-9))

        system.delete()

    def test_demag_asymptotic_radius(self):
        p1 = (0, 0, 0)
        p2 = (3e-9, 6e-9, 4e-9)
        cell = (1e-9, 2e-9, 4e-9)
        mesh = oc.Mesh(p1=p1, p2=p2, cell=cell)

        name = 'demag_asymptotic_radius'
        if os.path.exists(name):
            shutil.rmtree(name)

        Ms = 1e6

        system = oc.System(name=name)
        system.hamiltonian = oc.Demag(asymptotic_radius=6)
        system.m = df.Field(mesh, dim=3, value=(0, 0, 1), norm=Ms)

        md = oc.MinDriver()
        md.drive(system)

        system.delete()
