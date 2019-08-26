import os
import shutil
import random
import numpy as np
import oommfc as oc
import discretisedfield as df


class TestDamping:
    def setup(self):
        self.p1 = (-5e-9, -5e-9, -3e-9)
        self.p2 = (5e-9, 5e-9, 3e-9)
        self.n = (10, 10, 10)
        self.regions = {'r1': df.Region(p1=(-5e-9, -5e-9, -3e-9),
                                        p2=(5e-9, 0, 3e-9)),
                        'r2': df.Region(p1=(-5e-9, 0, -3e-9),
                                        p2=(5e-9, 5e-9, 3e-9))}

    def test_scalar(self):
        name = 'dp_scalar'
        if os.path.exists(name):
            shutil.rmtree(name)

        H = (0, 0, 1e6)
        alpha = 0
        Ms = 1e6

        mesh = oc.Mesh(p1=self.p1, p2=self.p2, n=self.n)

        system = oc.System(name=name)
        system.hamiltonian = oc.Zeeman(H=H)
        system.dynamics = oc.Damping(alpha=alpha)
        system.m = df.Field(mesh, dim=3, value=(0, 0.1, 1), norm=Ms)

        td = oc.TimeDriver()
        td.drive(system, t=0.2e-9, n=50)

        # Alpha is zero, nothing should change.
        value = system.m(mesh.random_point())
        assert np.linalg.norm(np.cross(value, (0, 0.1*Ms, Ms))) < 1e-3

        system.delete()

    def test_dict(self):
        name = 'dp_dict'
        if os.path.exists(name):
            shutil.rmtree(name)

        H = (0, 0, 1e6)
        alpha = {'r1': 0, 'r2': 1}
        Ms = 1e6

        mesh = oc.Mesh(p1=self.p1, p2=self.p2, n=self.n,
                       regions=self.regions)

        system = oc.System(name=name)
        system.hamiltonian = oc.Zeeman(H=H)
        system.dynamics = oc.Damping(alpha=alpha)
        system.m = df.Field(mesh, dim=3, value=(0, 0.1, 1), norm=Ms)

        td = oc.TimeDriver()
        td.drive(system, t=0.2e-9, n=50)

        # alpha=0 region
        value = system.m((1e-9, -4e-9, 3e-9))
        assert np.linalg.norm(np.cross(value, (0, 0.1*Ms, Ms))) < 1e-3

        # alpha!=0 region
        value = system.m((1e-9, 4e-9, 3e-9))
        assert np.linalg.norm(np.subtract(value, (0, 0, Ms))) < 1e-3

        system.delete()

    def test_field(self):
        name = 'dp_field'
        if os.path.exists(name):
            shutil.rmtree(name)

        mesh = oc.Mesh(p1=self.p1, p2=self.p2, n=self.n)

        def value_fun(pos):
            x, y, z = pos
            if y <= 0:
                return 0
            else:
                return 1

        H = (0, 0, 1e6)
        alpha = df.Field(mesh, dim=1, value=value_fun)
        Ms = 1e6

        system = oc.System(name=name)
        system.hamiltonian = oc.Zeeman(H=H)
        system.dynamics = oc.Damping(alpha=alpha)
        system.m = df.Field(mesh, dim=3, value=(0, 0.1, 1), norm=Ms)

        td = oc.TimeDriver()
        td.drive(system, t=0.2e-9, n=50)

        # alpha=0 region
        value = system.m((1e-9, -4e-9, 3e-9))
        assert np.linalg.norm(np.cross(value, (0, 0.1*Ms, Ms))) < 1e-3

        # alpha!=0 region
        value = system.m((1e-9, 4e-9, 3e-9))
        assert np.linalg.norm(np.subtract(value, (0, 0, Ms))) < 1e-3

        system.delete()
