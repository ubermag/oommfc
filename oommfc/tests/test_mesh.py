import os
import shutil
import numpy as np
import oommfc as oc
import discretisedfield as df


class TestMesh:
    def setup(self):
        self.p1 = (-7e-9, -5e-9, -4e-9)
        self.p2 = (7e-9, 5e-9, 4e-9)
        self.cell = (1e-9, 1e-9, 1e-9)
        self.pbc = 'xyz'
        self.regions = {'r1': df.Region(p1=(-7e-9, -5e-9, -4e-9),
                                        p2=(7e-9, 0, 4e-9)),
                        'r2': df.Region(p1=(-7e-9, 0, -4e-9),
                                        p2=(7e-9, 2e-9, 4e-9)),
                        'r3': df.Region(p1=(-7e-9, 2e-9, -4e-9),
                                        p2=(7e-9, 5e-9, 4e-9))}

    def test_single_nopbc(self):
        name = 'mh_single_nopbc'
        if os.path.exists(name):
            shutil.rmtree(name)

        Ms = 1e6
        H = (0, 0, 5e6)

        mesh = oc.Mesh(p1=self.p1, p2=self.p2, cell=self.cell)

        system = oc.System(name=name)
        system.hamiltonian = oc.Zeeman(H=H)
        system.m = df.Field(mesh, dim=3, value=(1, 0, 0), norm=Ms)

        md = oc.MinDriver()
        md.drive(system)

        value = system.m(mesh.random_point())
        assert np.linalg.norm(np.subtract(value, (0, 0, Ms))) < 1e-3

        if os.path.exists(name):
            shutil.rmtree(name)

    def test_multi_nopbc(self):
        name = 'mh_multi_nopbc'
        if os.path.exists(name):
            shutil.rmtree(name)

        Ms = 1e6
        H = (0, 0, 5e6)

        mesh = oc.Mesh(p1=self.p1, p2=self.p2,
                       cell=self.cell, regions=self.regions)

        system = oc.System(name=name)
        system.hamiltonian = oc.Zeeman(H=H)
        system.m = df.Field(mesh, dim=3, value=(1, 0, 0), norm=Ms)

        md = oc.MinDriver()
        md.drive(system)

        value = system.m(mesh.random_point())
        assert np.linalg.norm(np.subtract(value, (0, 0, Ms))) < 1e-3

        if os.path.exists(name):
            shutil.rmtree(name)

    def test_single_pbc(self):
        name = 'mh_single_pbc'
        if os.path.exists(name):
            shutil.rmtree(name)

        Ms = 1e6
        H = (0, 0, 5e6)

        mesh = oc.Mesh(p1=self.p1, p2=self.p2, cell=self.cell, pbc=self.pbc)

        system = oc.System(name=name)
        system.hamiltonian = oc.Zeeman(H=H)
        system.m = df.Field(mesh, dim=3, value=(1, 0, 0), norm=Ms)

        md = oc.MinDriver()
        md.drive(system)

        value = system.m(mesh.random_point())
        assert np.linalg.norm(np.subtract(value, (0, 0, Ms))) < 1e-3

        if os.path.exists(name):
            shutil.rmtree(name)

    def test_multi_pbc(self):
        name = 'mh_multi_pbc'
        if os.path.exists(name):
            shutil.rmtree(name)

        Ms = 1e6
        H = (0, 0, 5e6)

        mesh = oc.Mesh(p1=self.p1, p2=self.p2, cell=self.cell,
                       pbc=self.pbc, regions=self.regions)

        system = oc.System(name=name)
        system.hamiltonian = oc.Zeeman(H=H)
        system.m = df.Field(mesh, dim=3, value=(1, 0, 0), norm=Ms)

        md = oc.MinDriver()
        md.drive(system)

        value = system.m(mesh.random_point())
        assert np.linalg.norm(np.subtract(value, (0, 0, Ms))) < 1e-3

        if os.path.exists(name):
            shutil.rmtree(name)
