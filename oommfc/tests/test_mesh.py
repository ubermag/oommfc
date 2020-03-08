import numpy as np
import oommfc as oc
import discretisedfield as df
import micromagneticmodel as mm


class TestMesh:
    def setup(self):
        p1 = (-7e-9, -5e-9, -4e-9)
        p2 = (7e-9, 5e-9, 4e-9)
        self.region = df.Region(p1=p1, p2=p2)
        self.cell = (1e-9, 1e-9, 1e-9)
        self.pbc = 'xyz'
        self.subregions = {'r1': df.Region(p1=(-7e-9, -5e-9, -4e-9),
                                           p2=(7e-9, 0, 4e-9)),
                           'r2': df.Region(p1=(-7e-9, 0, -4e-9),
                                           p2=(7e-9, 2e-9, 4e-9)),
                           'r3': df.Region(p1=(-7e-9, 2e-9, -4e-9),
                                           p2=(7e-9, 5e-9, 4e-9))}

    def test_single_nopbc(self):
        name = 'mesh_single_nopbc'

        Ms = 1e6
        H = (0, 0, 5e6)

        mesh = df.Mesh(region=self.region, cell=self.cell)

        system = mm.System(name=name)
        system.energy = mm.Zeeman(H=H)
        system.m = df.Field(mesh, dim=3, value=(1, 0, 0), norm=Ms)

        md = oc.MinDriver()
        md.drive(system)

        value = system.m(mesh.region.random_point())
        assert np.linalg.norm(np.subtract(value, (0, 0, Ms))) < 1e-3

    def test_multi_nopbc(self):
        name = 'mesh_multi_nopbc'

        Ms = 1e6
        H = (0, 0, 5e6)

        mesh = df.Mesh(region=self.region, cell=self.cell,
                       subregions=self.subregions)

        system = mm.System(name=name)
        system.energy = mm.Zeeman(H=H)
        system.m = df.Field(mesh, dim=3, value=(1, 0, 0), norm=Ms)

        md = oc.MinDriver()
        md.drive(system)

        value = system.m(mesh.region.random_point())
        assert np.linalg.norm(np.subtract(value, (0, 0, Ms))) < 1e-3

    def test_single_pbc(self):
        name = 'mesh_single_pbc'

        Ms = 1e6
        H = (0, 0, 5e6)

        mesh = df.Mesh(region=self.region, cell=self.cell, pbc=self.pbc)

        system = mm.System(name=name)
        system.energy = mm.Zeeman(H=H)
        system.m = df.Field(mesh, dim=3, value=(1, 0, 0), norm=Ms)

        md = oc.MinDriver()
        md.drive(system)

        value = system.m(mesh.region.random_point())
        assert np.linalg.norm(np.subtract(value, (0, 0, Ms))) < 1e-3

    def test_multi_pbc(self):
        name = 'mesh_multi_pbc'

        Ms = 1e6
        H = (0, 0, 5e6)

        mesh = df.Mesh(region=self.region, cell=self.cell,
                       pbc=self.pbc, subregions=self.subregions)

        system = mm.System(name=name)
        system.energy = mm.Zeeman(H=H)
        system.m = df.Field(mesh, dim=3, value=(1, 0, 0), norm=Ms)

        md = oc.MinDriver()
        md.drive(system)

        value = system.m(mesh.region.random_point())
        assert np.linalg.norm(np.subtract(value, (0, 0, Ms))) < 1e-3
