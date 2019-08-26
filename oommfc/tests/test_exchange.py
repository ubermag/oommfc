import os
import shutil
import random
import numpy as np
import oommfc as oc
import discretisedfield as df


class TestExchange:
    def setup(self):
        self.p1 = (-5e-9, -5e-9, -3e-9)
        self.p2 = (5e-9, 5e-9, 3e-9)
        self.n = (10, 10, 10)
        self.regions = {'r1': df.Region(p1=(-5e-9, -5e-9, -3e-9),
                                        p2=(5e-9, 0, 3e-9)),
                        'r2': df.Region(p1=(-5e-9, 0, -3e-9),
                                        p2=(5e-9, 5e-9, 3e-9))}

    def test_scalar(self):
        name = 'ex_scalar'
        if os.path.exists(name):
            shutil.rmtree(name)

        A = 1e-12
        Ms = 1e6

        mesh = oc.Mesh(p1=self.p1, p2=self.p2, n=self.n)

        system = oc.System(name=name)
        system.hamiltonian = oc.Exchange(A=A)

        def m_value(pos):
            return [2*random.random()-1 for i in range(3)]

        system.m = df.Field(mesh, dim=3, value=m_value, norm=Ms)

        md = oc.MinDriver()
        md.drive(system)

        assert abs(np.linalg.norm(system.m.average) - Ms) < 1e-3

        system.delete()

    def test_dict(self):
        name = 'ex_dict'
        if os.path.exists(name):
            shutil.rmtree(name)

        A = {'r1': 0, 'r2': 1e-12, 'r1:r2': 1e-12}
        Ms = 1e6

        mesh = oc.Mesh(p1=self.p1, p2=self.p2, n=self.n,
                       regions=self.regions)

        system = oc.System(name=name)
        system.hamiltonian = oc.Exchange(A=A)

        def m_value(pos):
            return [2*random.random()-1 for i in range(3)]

        system.m = df.Field(mesh, dim=3, value=m_value, norm=Ms)

        md = oc.MinDriver()
        md.drive(system)

        # A=0 region
        value1 = system.m((1e-9, -4e-9, 3e-9))
        value2 = system.m((1e-9, -2e-9, 3e-9))
        assert np.linalg.norm(np.subtract(value1, value2)) > 1

        # A!=0 region
        value1 = system.m((1e-9, 4e-9, 3e-9))
        value2 = system.m((1e-9, 2e-9, 3e-9))
        assert np.linalg.norm(np.subtract(value1, value2)) < 1

        system.delete()

    def test_field(self):
        name = 'ex_field'
        if os.path.exists(name):
            shutil.rmtree(name)

        mesh = oc.Mesh(p1=self.p1, p2=self.p2, n=self.n)

        def A_fun(pos):
            x, y, z = pos
            if x <= 0:
                return 1e-10  # for 0, OOMMF gives nan
            else:
                return 1e-12

        A = df.Field(mesh, dim=1, value=A_fun)
        Ms = 1e6

        system = oc.System(name=name)
        system.hamiltonian = oc.Exchange(A=A)

        def m_value(pos):
            return [2*random.random()-1 for i in range(3)]

        system.m = df.Field(mesh, dim=3, value=m_value, norm=Ms)

        md = oc.MinDriver()
        md.drive(system)

        assert abs(np.linalg.norm(system.m.average) - Ms) < 1e-3

        system.delete()
