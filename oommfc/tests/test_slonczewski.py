import numpy as np
import oommfc as oc
import discretisedfield as df
import micromagneticmodel as mm


class TestSlonczewski:
    def setup(self):
        p1 = (-5e-9, -5e-9, -3e-9)
        p2 = (5e-9, 5e-9, 3e-9)
        self.region = df.Region(p1=p1, p2=p2)
        self.n = (2, 2, 2)
        self.subregions = {'r1': df.Region(p1=(-5e-9, -5e-9, -3e-9),
                                           p2=(5e-9, 0, 3e-9)),
                           'r2': df.Region(p1=(-5e-9, 0, -3e-9),
                                           p2=(5e-9, 5e-9, 3e-9))}

    def test_single_values(self):
        name = 'slonczewski_scalar_values'

        J = 1e12
        mp = (1, 0, 0)
        P = 0.4
        Lambda = 2
        eps_prime = 0
        H = (0, 0, 1e6)
        Ms = 1e6

        mesh = df.Mesh(region=self.region, n=self.n)

        system = mm.System(name=name)
        system.energy = mm.Zeeman(H=H)
        system.dynamics = mm.Slonczewski(J=J, mp=mp, P=P, Lambda=Lambda,
                                         eps_prime=eps_prime)
        system.m = df.Field(mesh, dim=3, value=(0, 0.1, 1), norm=Ms)

        td = oc.TimeDriver()
        td.drive(system, t=0.2e-9, n=20)

        # Check if it runs.

    def test_dict_values(self):
        name = 'slonczewski_scalar_values'

        J = {'r1': 1e12, 'r2': 5e12}
        mp = {'r1': (0, 0, 1), 'r2': (0, 1, 0)}
        P = {'r1': 0.4, 'r2': 0.35}
        Lambda = {'r1': 2, 'r2': 1.5}
        eps_prime = {'r1': 0, 'r2': 1}
        H = (0, 0, 1e6)
        Ms = 1e6

        mesh = df.Mesh(region=self.region, n=self.n,
                       subregions=self.subregions)

        system = mm.System(name=name)
        system.energy = mm.Zeeman(H=H)
        system.dynamics = mm.Slonczewski(J=J, mp=mp, P=P, Lambda=Lambda,
                                         eps_prime=eps_prime)
        system.m = df.Field(mesh, dim=3, value=(0, 0.1, 1), norm=Ms)

        td = oc.TimeDriver()
        td.drive(system, t=0.2e-9, n=20)

        # Check if it runs.

    def test_field_values(self):
        name = 'slonczewski_scalar_values'

        mesh = df.Mesh(region=self.region, n=self.n)

        J = df.Field(mesh, dim=1, value=0.5e12)
        mp = df.Field(mesh, dim=3, value=(1, 0, 0))
        P = df.Field(mesh, dim=1, value=0.5)
        Lambda = df.Field(mesh, dim=1, value=2)
        eps_prime = df.Field(mesh, dim=1, value=1)
        H = (0, 0, 1e6)
        Ms = 1e6

        system = mm.System(name=name)
        system.energy = mm.Zeeman(H=H)
        system.dynamics = mm.Slonczewski(J=J, mp=mp, P=P, Lambda=Lambda,
                                         eps_prime=eps_prime)
        system.m = df.Field(mesh, dim=3, value=(0, 0.1, 1), norm=Ms)

        td = oc.TimeDriver()
        td.drive(system, t=0.2e-9, n=20)

        # Check if it runs.
