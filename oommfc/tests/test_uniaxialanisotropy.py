import numpy as np
import oommfc as oc
import discretisedfield as df
import micromagneticmodel as mm


class TestUniaxialAnisotropy:
    def setup(self):
        p1 = (-7e-9, -5e-9, -4e-9)
        p2 = (7e-9, 5e-9, 4e-9)
        self.region = df.Region(p1=p1, p2=p2)
        self.cell = (1e-9, 1e-9, 1e-9)
        self.subregions = {'r1': df.Region(p1=(-7e-9, -5e-9, -4e-9),
                                           p2=(0, 5e-9, 4e-9)),
                           'r2': df.Region(p1=(0, -5e-9, -4e-9),
                                           p2=(7e-9, 5e-9, 4e-9))}

    def test_scalar_vector(self):
        name = 'uniaxialanisotropy_scalar_vector'

        K = 1e5
        u = (0, 0, 1)
        Ms = 1e6

        system = mm.System(name=name)
        system.energy = mm.UniaxialAnisotropy(K=K, u=u)

        mesh = df.Mesh(region=self.region, cell=self.cell)
        system.m = df.Field(mesh, dim=3, value=(0, 0.3, 1), norm=Ms)

        md = oc.MinDriver()
        md.drive(system)

        value = system.m(mesh.region.random_point())
        assert np.linalg.norm(np.subtract(value, (0, 0, Ms))) < 1e-3

    def test_field_vector(self):
        name = 'uniaxialanisotropy_field_vector'

        def value_fun(pos):
            x, y, z = pos
            if x <= 0:
                return 0
            else:
                return 1e5

        mesh = df.Mesh(region=self.region, cell=self.cell)

        K = df.Field(mesh, dim=1, value=value_fun)
        u = (0, 0, 1)
        Ms = 1e6

        system = mm.System(name=name)
        system.energy = mm.UniaxialAnisotropy(K=K, u=u)
        system.m = df.Field(mesh, dim=3, value=(0, 0.3, 1), norm=Ms)

        md = oc.MinDriver()
        md.drive(system)

        value = system.m((-2e-9, -2e-9, -2e-9))
        assert np.linalg.norm(np.cross(value, (0, 0.3*Ms, Ms))) < 1e-3

        value = system.m((2e-9, 2e-9, 2e-9))
        assert np.linalg.norm(np.subtract(value, (0, 0, Ms))) < 1e-3

    def test_scalar_field(self):
        name = 'uniaxialanisotropy_scalar_field'

        def value_fun(pos):
            x, y, z = pos
            if x <= 0:
                return (1, 0, 0)
            else:
                return (0, 1, 0)

        mesh = df.Mesh(region=self.region, cell=self.cell)

        K = 1e5
        u = df.Field(mesh, dim=3, value=value_fun)
        Ms = 1e6

        system = mm.System(name=name)
        system.energy = mm.UniaxialAnisotropy(K=K, u=u)
        system.m = df.Field(mesh, dim=3, value=(1, 1, 0), norm=Ms)

        md = oc.MinDriver()
        md.drive(system)

        value = system.m((-2e-9, -2e-9, -2e-9))
        assert np.linalg.norm(np.subtract(value, (Ms, 0, 0))) < 1e-3

        value = system.m((2e-9, 2e-9, 2e-9))
        assert np.linalg.norm(np.subtract(value, (0, Ms, 0))) < 1e-3

    def test_field_field(self):
        name = 'uniaxialanisotropy_field_field'

        def K_fun(pos):
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

        mesh = df.Mesh(region=self.region, cell=self.cell)

        K = df.Field(mesh, dim=1, value=K_fun)
        u = df.Field(mesh, dim=3, value=u_fun)
        Ms = 1e6

        system = mm.System(name=name)
        system.energy = mm.UniaxialAnisotropy(K=K, u=u)
        system.m = df.Field(mesh, dim=3, value=(1, 1, 0), norm=Ms)

        md = oc.MinDriver()
        md.drive(system)

        value = system.m((-3e-9, -3e-9, -3e-9))
        assert np.linalg.norm(np.subtract(value, (Ms, 0, 0))) < 1e-3

        value = system.m((3e-9, 3e-9, 3e-9))
        assert np.linalg.norm(np.subtract(value, (0, Ms, 0))) < 1e-3

        value = system.m((0, 0, 0))
        assert np.linalg.norm(np.cross(value, (Ms, Ms, 0))) < 1e-3

    def test_dict_vector(self):
        name = 'uniaxialanisotropy_dict_vector'

        mesh = df.Mesh(region=self.region, cell=self.cell,
                       subregions=self.subregions)
        K = {'r1': 0, 'r2': 1e5}
        u = (0, 0, 1)
        Ms = 1e6

        system = mm.System(name=name)
        system.energy = mm.UniaxialAnisotropy(K=K, u=u)
        system.m = df.Field(mesh, dim=3, value=(0, 0.3, 1), norm=Ms)

        md = oc.MinDriver()
        md.drive(system)

        value = system.m((-2e-9, -2e-9, -2e-9))
        assert np.linalg.norm(np.cross(value, (0, 0.3*Ms, Ms))) < 1e-3

        value = system.m((2e-9, 2e-9, 2e-9))
        assert np.linalg.norm(np.subtract(value, (0, 0, Ms))) < 1e-3

    def test_field_dict(self):
        name = 'uniaxialanisotropy_field_dict'

        def K_fun(pos):
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

        mesh = df.Mesh(region=self.region, cell=self.cell)

        K = df.Field(mesh, dim=1, value=K_fun)
        u = df.Field(mesh, dim=3, value=u_fun)
        Ms = 1e6

        system = mm.System(name=name)
        system.energy = mm.UniaxialAnisotropy(K=K, u=u)
        system.m = df.Field(mesh, dim=3, value=(1, 1, 0), norm=Ms)

        md = oc.MinDriver()
        md.drive(system)

        value = system.m((-3e-9, -3e-9, -3e-9))
        assert np.linalg.norm(np.subtract(value, (Ms, 0, 0))) < 1e-3

        value = system.m((3e-9, 3e-9, 3e-9))
        assert np.linalg.norm(np.subtract(value, (0, Ms, 0))) < 1e-3

        value = system.m((0, 0, 0))
        assert np.linalg.norm(np.cross(value, (Ms, Ms, 0))) < 1e-3
