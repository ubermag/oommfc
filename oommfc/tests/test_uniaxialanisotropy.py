import os
import shutil
import numpy as np
import oommfc as oc
import discretisedfield as df


class TestUniaxialAnisotropy:
    def setup(self):
        self.p1 = (-7e-9, -5e-9, -4e-9)
        self.p2 = (7e-9, 5e-9, 4e-9)
        self.cell = (1e-9, 1e-9, 1e-9)
        self.regions = {'r1': df.Region(p1=(-7e-9, -5e-9, -4e-9),
                                        p2=(0, 5e-9, 4e-9)),
                        'r2': df.Region(p1=(0, -5e-9, -4e-9),
                                        p2=(7e-9, 5e-9, 4e-9))}

    def test_scalar_vector(self):
        name = 'ua_scalar_vector'
        if os.path.exists(name):
            shutil.rmtree(name)

        K1 = 1e5
        u = (0, 0, 1)
        Ms = 1e6

        mesh = oc.Mesh(p1=self.p1, p2=self.p2, cell=self.cell)

        system = oc.System(name=name)
        system.hamiltonian = oc.UniaxialAnisotropy(K1=K1, u=u)
        system.m = df.Field(mesh, dim=3, value=(0, 0.3, 1), norm=Ms)

        md = oc.MinDriver()
        md.drive(system)

        value = system.m(mesh.random_point())
        assert np.linalg.norm(np.subtract(value, (0, 0, Ms))) < 1e-3

        system.delete()

    def test_field_vector(self):
        name = 'ua_field_vector'
        if os.path.exists(name):
            shutil.rmtree(name)

        def value_fun(pos):
            x, y, z = pos
            if x <= 0:
                return 0
            else:
                return 1e5

        mesh = oc.Mesh(p1=self.p1, p2=self.p2, cell=self.cell)

        K1 = df.Field(mesh, dim=1, value=value_fun)
        u = (0, 0, 1)
        Ms = 1e6

        system = oc.System(name=name)
        system.hamiltonian = oc.UniaxialAnisotropy(K1=K1, u=u)
        system.m = df.Field(mesh, dim=3, value=(0, 0.3, 1), norm=Ms)

        md = oc.MinDriver()
        md.drive(system)

        value = system.m((-2e-9, -2e-9, -2e-9))
        assert np.linalg.norm(np.cross(value, (0, 0.3*Ms, Ms))) < 1e-3

        value = system.m((2e-9, 2e-9, 2e-9))
        assert np.linalg.norm(np.subtract(value, (0, 0, Ms))) < 1e-3

        system.delete()

    def test_scalar_field(self):
        name = 'ua_scalar_field'
        if os.path.exists(name):
            shutil.rmtree(name)

        def value_fun(pos):
            x, y, z = pos
            if x <= 0:
                return (1, 0, 0)
            else:
                return (0, 1, 0)

        mesh = oc.Mesh(p1=self.p1, p2=self.p2, cell=self.cell)

        K1 = 1e5
        u = df.Field(mesh, dim=3, value=value_fun)
        Ms = 1e6

        system = oc.System(name=name)
        system.hamiltonian = oc.UniaxialAnisotropy(K1=K1, u=u)
        system.m = df.Field(mesh, dim=3, value=(1, 1, 0), norm=Ms)

        md = oc.MinDriver()
        md.drive(system)

        value = system.m((-2e-9, -2e-9, -2e-9))
        assert np.linalg.norm(np.subtract(value, (Ms, 0, 0))) < 1e-3

        value = system.m((2e-9, 2e-9, 2e-9))
        assert np.linalg.norm(np.subtract(value, (0, Ms, 0))) < 1e-3

        system.delete()

    def test_field_field(self):
        name = 'ua_field_field'
        if os.path.exists(name):
            shutil.rmtree(name)

        def K1_fun(pos):
            x, y, z = pos
            if -2e-9 <= x <= 2e-9:
                return 0
            else:
                return 1e5

        def u_fun(pos):
            x, y, z = pos
            if x <= 0:
                return (1, 0, 0)
            else:
                return (0, 1, 0)

        mesh = oc.Mesh(p1=self.p1, p2=self.p2, cell=self.cell)

        K1 = df.Field(mesh, dim=1, value=K1_fun)
        u = df.Field(mesh, dim=3, value=u_fun)
        Ms = 1e6

        system = oc.System(name=name)
        system.hamiltonian = oc.UniaxialAnisotropy(K1=K1, u=u)
        system.m = df.Field(mesh, dim=3, value=(1, 1, 0), norm=Ms)

        md = oc.MinDriver()
        md.drive(system)

        value = system.m((-3e-9, -3e-9, -3e-9))
        assert np.linalg.norm(np.subtract(value, (Ms, 0, 0))) < 1e-3

        value = system.m((3e-9, 3e-9, 3e-9))
        assert np.linalg.norm(np.subtract(value, (0, Ms, 0))) < 1e-3

        value = system.m((0, 0, 0))
        assert np.linalg.norm(np.cross(value, (Ms, Ms, 0))) < 1e-3

        system.delete()

    def test_dict_vector(self):
        name = 'ua_dict_vector'
        if os.path.exists(name):
            shutil.rmtree(name)

        mesh = oc.Mesh(p1=self.p1, p2=self.p2, cell=self.cell,
                       regions=self.regions)
        K1 = {'r1': 0, 'r2': 1e5}
        u = (0, 0, 1)
        Ms = 1e6

        system = oc.System(name=name)
        system.hamiltonian = oc.UniaxialAnisotropy(K1=K1, u=u)
        system.m = df.Field(mesh, dim=3, value=(0, 0.3, 1), norm=Ms)

        md = oc.MinDriver()
        md.drive(system)

        value = system.m((-2e-9, -2e-9, -2e-9))
        assert np.linalg.norm(np.cross(value, (0, 0.3*Ms, Ms))) < 1e-3

        value = system.m((2e-9, 2e-9, 2e-9))
        assert np.linalg.norm(np.subtract(value, (0, 0, Ms))) < 1e-3

        system.delete()

    def test_field_dict(self):
        name = 'ua_field_dict'
        if os.path.exists(name):
            shutil.rmtree(name)

        def K1_fun(pos):
            x, y, z = pos
            if -2e-9 <= x <= 2e-9:
                return 0
            else:
                return 1e5

        def u_fun(pos):
            x, y, z = pos
            if x <= 0:
                return (1, 0, 0)
            else:
                return (0, 1, 0)

        mesh = oc.Mesh(p1=self.p1, p2=self.p2, cell=self.cell)

        K1 = df.Field(mesh, dim=1, value=K1_fun)
        u = df.Field(mesh, dim=3, value=u_fun)
        Ms = 1e6

        system = oc.System(name=name)
        system.hamiltonian = oc.UniaxialAnisotropy(K1=K1, u=u)
        system.m = df.Field(mesh, dim=3, value=(1, 1, 0), norm=Ms)

        md = oc.MinDriver()
        md.drive(system)

        value = system.m((-3e-9, -3e-9, -3e-9))
        assert np.linalg.norm(np.subtract(value, (Ms, 0, 0))) < 1e-3

        value = system.m((3e-9, 3e-9, 3e-9))
        assert np.linalg.norm(np.subtract(value, (0, Ms, 0))) < 1e-3

        value = system.m((0, 0, 0))
        assert np.linalg.norm(np.cross(value, (Ms, Ms, 0))) < 1e-3

        system.delete()
