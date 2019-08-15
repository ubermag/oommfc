import os
import shutil
import numpy as np
import oommfc as oc
import discretisedfield as df


class TestZeeman:
    def setup(self):
        p1 = (-10e-9, -5e-9, -3e-9)
        p2 = (10e-9, 5e-9, 3e-9)
        cell = (1e-9, 1e-9, 1e-9)
        self.mesh = oc.Mesh(p1=p1, p2=p2, cell=cell)

    def test_vector(self):
        name = 'ze_vector'
        if os.path.exists(name):
            shutil.rmtree(name)

        H = (0, 0, 1e6)
        Ms = 1e6

        system = oc.System(name=name)
        system.hamiltonian = oc.Zeeman(H=H)
        system.m = df.Field(self.mesh, dim=3, value=(0, 1, 0), norm=Ms)

        md = oc.MinDriver()
        md.drive(system)

        value = system.m(self.mesh.random_point())
        assert np.linalg.norm(np.subtract(value, (0, 0, Ms))) < 1e-3

        if os.path.exists(name):
            shutil.rmtree(name)

    def test_field(self):
        name = 'ze_field'
        if os.path.exists(name):
            shutil.rmtree(name)

        def value_fun(pos):
            x, y, z = pos
            if x <= 0:
                return (1e6, 0, 0)
            else:
                return (0, 0, 1e6)

        H = df.Field(self.mesh, dim=3, value=value_fun)
        Ms = 1e6

        system = oc.System(name=name)
        system.hamiltonian = oc.Zeeman(H=H)
        system.m = df.Field(self.mesh, dim=3, value=(0, 1, 0), norm=Ms)

        md = oc.MinDriver()
        md.drive(system)

        value = system.m((-2e-9, -2e-9, -2e-9))
        assert np.linalg.norm(np.subtract(value, (Ms, 0, 0))) < 1e-3

        value = system.m((2e-9, 2e-9, 2e-9))
        assert np.linalg.norm(np.subtract(value, (0, 0, Ms))) < 1e-3

        if os.path.exists(name):
            shutil.rmtree(name)
