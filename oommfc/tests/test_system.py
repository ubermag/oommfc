import os
import shutil
import numpy as np
import oommfc as oc
import discretisedfield as df


class TestSystem:
    def setup(self):
        self.p1 = (-5e-9, -5e-9, -3e-9)
        self.p2 = (5e-9, 5e-9, 3e-9)
        self.n = (10, 10, 10)

    def test_system(self):
        name = 'test_system'
        if os.path.exists(name):
            shutil.rmtree(name)

        mesh = oc.Mesh(p1=self.p1, p2=self.p2, n=self.n)

        A = 1e-12
        H = (0, 0, 1e7)
        Ms = 1e6

        system = oc.System(name=name)
        system.hamiltonian = oc.Zeeman(H=H) + oc.Exchange(A=A)
        system.dynamics = oc.Damping(alpha=1)
        system.m = df.Field(mesh, dim=3, value=(0, 0.1, 1), norm=Ms)

        td = oc.TimeDriver()
        td.drive(system, t=0.5e-9, n=50)

        # u is zero, nothing should change.
        value = system.m(mesh.random_point())
        assert np.linalg.norm(np.subtract(value, (0, 0, Ms))) < 1e-3

        system.delete()
