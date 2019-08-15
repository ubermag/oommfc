import os
import shutil
import numpy as np
import oommfc as oc
import discretisedfield as df


class TestUniaxialAnisotropy:
    def setup(self):
        p1 = (-7e-9, -5e-9, -4e-9)
        p2 = (7e-9, 5e-9, 4e-9)
        cell = (1e-9, 1e-9, 1e-9)
        self.mesh = oc.Mesh(p1=p1, p2=p2, cell=cell)

    def test_scalar_vector(self):
        name = 'ua_scalar_vector'
        if os.path.exists(name):
            shutil.rmtree(name)
        
        K1 = 1e5
        u = (0, 0, 1)
        Ms = 1e6

        system = oc.System(name=name)
        system.hamiltonian = oc.UniaxialAnisotropy(K1=K1, u=u)
        system.m = df.Field(self.mesh, dim=3, value=(0, 0.3, 1), norm=Ms)

        md = oc.MinDriver()
        md.drive(system)

        value = system.m(self.mesh.random_point())
        assert np.linalg.norm(np.subtract(value, (0, 0, Ms))) < 1e-3

        if os.path.exists(name):
            shutil.rmtree(name)

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

        K1 = df.Field(self.mesh, dim=1, value=value_fun)
        u = (0, 0, 1)
        Ms = 1e6

        system = oc.System(name=name)
        system.hamiltonian = oc.UniaxialAnisotropy(K1=K1, u=u)
        system.m = df.Field(self.mesh, dim=3, value=(0, 0.3, 1), norm=Ms)

        md = oc.MinDriver()
        md.drive(system)

        value = system.m((-2e-9, -2e-9, -2e-9))
        assert np.linalg.norm(np.cross(value, (0, 0.3*Ms, Ms))) < 1e-3

        value = system.m((2e-9, 2e-9, 2e-9))
        assert np.linalg.norm(np.subtract(value, (0, 0, Ms))) < 1e-3

        if os.path.exists(name):
            shutil.rmtree(name)

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

        K1 = 1e5
        u = df.Field(self.mesh, dim=3, value=value_fun)
        Ms = 1e6

        system = oc.System(name=name)
        system.hamiltonian = oc.UniaxialAnisotropy(K1=K1, u=u)
        system.m = df.Field(self.mesh, dim=3, value=(1, 1, 0), norm=Ms)

        md = oc.MinDriver()
        md.drive(system)

        value = system.m((-2e-9, -2e-9, -2e-9))
        assert np.linalg.norm(np.subtract(value, (Ms, 0, 0))) < 1e-3

        value = system.m((2e-9, 2e-9, 2e-9))
        assert np.linalg.norm(np.subtract(value, (0, Ms, 0))) < 1e-3

        if os.path.exists(name):
            shutil.rmtree(name)

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

        K1 = df.Field(self.mesh, dim=1, value=K1_fun)
        u = df.Field(self.mesh, dim=3, value=u_fun)
        Ms = 1e6

        system = oc.System(name=name)
        system.hamiltonian = oc.UniaxialAnisotropy(K1=K1, u=u)
        system.m = df.Field(self.mesh, dim=3, value=(1, 1, 0), norm=Ms)

        md = oc.MinDriver()
        md.drive(system)

        value = system.m((-3e-9, -3e-9, -3e-9))
        assert np.linalg.norm(np.subtract(value, (Ms, 0, 0))) < 1e-3

        value = system.m((3e-9, 3e-9, 3e-9))
        assert np.linalg.norm(np.subtract(value, (0, Ms, 0))) < 1e-3

        value = system.m((0, 0, 0))
        assert np.linalg.norm(np.cross(value, (Ms, Ms, 0))) < 1e-3

        if os.path.exists(name):
            shutil.rmtree(name)
