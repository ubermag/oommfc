import numpy as np
import oommfc as oc
import discretisedfield as df
import micromagneticmodel as mm


class TestPrecession:
    def setup(self):
        p1 = (-5e-9, -5e-9, -3e-9)
        p2 = (5e-9, 5e-9, 3e-9)
        self.region = df.Region(p1=p1, p2=p2)
        self.n = (10, 10, 10)
        self.subregions = {'r1': df.Region(p1=(-5e-9, -5e-9, -3e-9),
                                           p2=(5e-9, 0, 3e-9)),
                           'r2': df.Region(p1=(-5e-9, 0, -3e-9),
                                           p2=(5e-9, 5e-9, 3e-9))}

    def test_scalar(self):
        name = 'precession_scalar'

        H = (0, 0, 1e6)
        gamma0 = 0
        Ms = 1e6

        mesh = df.Mesh(region=self.region, n=self.n)

        system = mm.System(name=name)
        system.energy = mm.Zeeman(H=H)
        system.dynamics = mm.Precession(gamma0=gamma0)
        system.m = df.Field(mesh, dim=3, value=(0, 0.1, 1), norm=Ms)

        td = oc.TimeDriver()
        td.drive(system, t=0.2e-9, n=50)

        # Gamma is zero, nothing should change.
        value = system.m(mesh.region.random_point())
        assert np.linalg.norm(np.cross(value, (0, 0.1*Ms, Ms))) < 1e-3

    def test_dict(self):
        name = 'precession_dict'

        H = (0, 0, 1e6)
        gamma0 = {'r1': 0, 'r2': 2.211e5}
        Ms = 1e6

        mesh = df.Mesh(region=self.region, n=self.n,
                       subregions=self.subregions)

        system = mm.System(name=name)
        system.energy = mm.Zeeman(H=H)
        system.dynamics = mm.Precession(gamma0=gamma0)
        system.m = df.Field(mesh, dim=3, value=(0, 0.1, 1), norm=Ms)

        td = oc.TimeDriver()
        td.drive(system, t=0.2e-9, n=50)

        # gamma=0 region
        value = system.m((1e-9, -4e-9, 3e-9))
        assert np.linalg.norm(np.cross(value, (0, 0.1*Ms, Ms))) < 1e-3

        # gamma!=0 region
        value = system.m((1e-9, 4e-9, 3e-9))
        assert np.linalg.norm(np.cross(value, (0, 0.1*Ms, Ms))) > 1

    def test_field(self):
        name = 'precession_field'

        mesh = df.Mesh(region=self.region, n=self.n)

        def value_fun(pos):
            x, y, z = pos
            if y <= 0:
                return 0
            else:
                return 2.211e5

        H = (0, 0, 1e6)
        gamma0 = df.Field(mesh, dim=1, value=value_fun)
        Ms = 1e6

        system = mm.System(name=name)
        system.energy = mm.Zeeman(H=H)
        system.dynamics = mm.Precession(gamma0=gamma0)
        system.m = df.Field(mesh, dim=3, value=(0, 0.1, 1), norm=Ms)

        td = oc.TimeDriver()
        td.drive(system, t=0.2e-9, n=50)

        # gamma=0 region
        value = system.m((1e-9, -4e-9, 3e-9))
        assert np.linalg.norm(np.cross(value, (0, 0.1*Ms, Ms))) < 1e-3

        # gamma!=0 region
        value = system.m((1e-9, 4e-9, 3e-9))
        assert np.linalg.norm(np.cross(value, (0, 0.1*Ms, Ms))) > 1
