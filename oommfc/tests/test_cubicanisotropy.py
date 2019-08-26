import os
import shutil
import numpy as np
import oommfc as oc
import discretisedfield as df


class TestCubicAnisotropy:
    def setup(self):
        self.p1 = (-7e-9, 0, 0)
        self.p2 = (7e-9, 5e-9, 4e-9)
        self.cell = (1e-9, 1e-9, 2e-9)
        self.regions = {'r1': df.Region(p1=(-7e-9, 0, 0), p2=(0, 5e-9, 4e-9)),
                        'r2': df.Region(p1=(0, 0, 0), p2=(7e-9, 5e-9, 4e-9))}

    def test_scalar_vector_vector(self):
        name = 'ca_scalar_vector_vector'
        if os.path.exists(name):
            shutil.rmtree(name)

        mesh = oc.Mesh(p1=self.p1, p2=self.p2, cell=self.cell)

        K1 = 1e5
        u1 = (0, 0, 1)
        u2 = (0, 1, 0)
        Ms = 1e6

        system = oc.System(name=name)
        system.hamiltonian = oc.CubicAnisotropy(K1=K1, u1=u1, u2=u2)

        def m_fun(pos):
            x, y, z = pos
            if x <= 0:
                return (0, 0.2, 1)
            else:
                return (0, 1, 0.2)

        system.m = df.Field(mesh, dim=3, value=m_fun, norm=Ms)

        md = oc.MinDriver()
        md.drive(system)

        value = system.m((-1e-9, 2e-9, 2e-9))
        assert np.linalg.norm(np.subtract(value, (0, 0, Ms))) < 1e-3

        value = system.m((1e-9, 2e-9, 2e-9))
        assert np.linalg.norm(np.subtract(value, (0, Ms, 0))) < 1e-3

        system.delete()

    def test_field_vector_vector(self):
        name = 'ca_field_vector_vector'
        if os.path.exists(name):
            shutil.rmtree(name)

        mesh = oc.Mesh(p1=self.p1, p2=self.p2, cell=self.cell)

        def K1_fun(pos):
            x, y, z = pos
            if x <= 0:
                return 0
            else:
                return 1e5

        K1 = df.Field(mesh, dim=1, value=K1_fun)
        u1 = (0, 0, 1)
        u2 = (0, 1, 0)
        Ms = 1e6

        system = oc.System(name=name)
        system.hamiltonian = oc.CubicAnisotropy(K1=K1, u1=u1, u2=u2)
        system.m = df.Field(mesh, dim=3, value=(0, 0.3, 1), norm=Ms)

        md = oc.MinDriver()
        md.drive(system)

        value = system.m((-2e-9, 1e-9, 1e-9))
        assert np.linalg.norm(np.cross(value, (0, 0.3*Ms, Ms))) < 1e-3

        value = system.m((2e-9, 2e-9, 2e-9))
        assert np.linalg.norm(np.subtract(value, (0, 0, Ms))) < 1e-3

        system.delete()

    def test_field_field_field(self):
        name = 'ca_field_field_field'
        if os.path.exists(name):
            shutil.rmtree(name)

        mesh = oc.Mesh(p1=self.p1, p2=self.p2, cell=self.cell)

        def K1_fun(pos):
            x, y, z = pos
            if -2e-9 <= x <= 2e-9:
                return 0
            else:
                return 1e5

        def u1_fun(pos):
            x, y, z = pos
            if x <= 0:
                return (0, 1, 0)
            else:
                return (0, 0, 1)

        def u2_fun(pos):
            x, y, z = pos
            if x <= 0:
                return (0, 0, 1)
            else:
                return (0, 1, 0)

        K1 = df.Field(mesh, dim=1, value=K1_fun)
        u1 = df.Field(mesh, dim=3, value=u1_fun)
        u2 = df.Field(mesh, dim=3, value=u2_fun)
        Ms = 1e6

        system = oc.System(name=name)
        system.hamiltonian = oc.CubicAnisotropy(K1=K1, u1=u1, u2=u2)
        system.m = df.Field(mesh, dim=3, value=(0, 0.3, 1), norm=Ms)

        md = oc.MinDriver()
        md.drive(system)

        value = system.m((0, 0, 0))
        assert np.linalg.norm(np.cross(value, (0, 0.3*Ms, Ms))) < 1e-3

        value = system.m((3e-9, 2e-9, 2e-9))
        assert np.linalg.norm(np.subtract(value, (0, 0, Ms))) < 1e-3

        value = system.m((-3e-9, 2e-9, 2e-9))
        assert np.linalg.norm(np.subtract(value, (0, 0, Ms))) < 1e-3

        system.delete()

    def test_dict_vector_vector(self):
        name = 'ca_dict_vector_vector'
        if os.path.exists(name):
            shutil.rmtree(name)

        mesh = oc.Mesh(p1=self.p1, p2=self.p2, cell=self.cell,
                       regions=self.regions)

        K1 = {'r1': 0, 'r2': 1e5}
        u1 = (0, 0, 1)
        u2 = (0, 1, 0)
        Ms = 1e6

        system = oc.System(name=name)
        system.hamiltonian = oc.CubicAnisotropy(K1=K1, u1=u1, u2=u2)
        system.m = df.Field(mesh, dim=3, value=(0, 0.3, 1), norm=Ms)

        md = oc.MinDriver()
        md.drive(system)

        value = system.m((-2e-9, 1e-9, 1e-9))
        assert np.linalg.norm(np.cross(value, (0, 0.3*Ms, Ms))) < 1e-3

        value = system.m((2e-9, 2e-9, 2e-9))
        assert np.linalg.norm(np.subtract(value, (0, 0, Ms))) < 1e-3

        system.delete()
