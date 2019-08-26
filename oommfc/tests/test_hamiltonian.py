import os
import shutil
import numpy as np
import oommfc as oc
import discretisedfield as df


class TestHamiltonian:
    def setup(self):
        self.p1 = (0, 0, 0)
        self.p2 = (10e-9, 5e-9, 3e-9)
        self.cell = (1e-9, 1e-9, 1e-9)
        self.regions = {'r1': df.Region(p1=(0, 0, 0),
                                        p2=(5e-9, 5e-9, 3e-9)),
                        'r2': df.Region(p1=(5e-9, 0, 0),
                                        p2=(10e-9, 5e-9, 3e-9))}

    def test_exchange_zeeman(self):
        name = 'hm_exchange_zeeman'
        if os.path.exists(name):
            shutil.rmtree(name)

        A = 1e-12
        H = (1e6, 0, 0)
        Ms = 1e6

        mesh = oc.Mesh(p1=self.p1, p2=self.p2, cell=self.cell)

        system = oc.System(name=name)
        system.hamiltonian = oc.Exchange(A=A) + oc.Zeeman(H=H)
        system.m = df.Field(mesh, dim=3, value=(0, 1, 0), norm=Ms)

        md = oc.MinDriver()
        md.drive(system)

        value = system.m(mesh.random_point())
        assert np.linalg.norm(np.subtract(value, (Ms, 0, 0))) < 1e-3

        system.delete()

    def test_exchange_uniaxialanisotropy(self):
        name = 'hm_exchange_uniaxialanisotropy'
        if os.path.exists(name):
            shutil.rmtree(name)

        A = {'r1': 1e-12, 'r2': 0}
        K1 = 1e5
        u = (1, 0, 0)
        Ms = 1e6

        mesh = oc.Mesh(p1=self.p1, p2=self.p2, cell=self.cell,
                       regions=self.regions)

        system = oc.System(name=name)
        system.hamiltonian = oc.Exchange(A=A) + \
            oc.UniaxialAnisotropy(K1=K1, u=u)
        system.m = df.Field(mesh, dim=3, value=(0.5, 1, 0), norm=Ms)

        md = oc.MinDriver()
        md.drive(system)

        value = system.m(mesh.random_point())
        assert np.linalg.norm(np.subtract(value, (Ms, 0, 0))) < 1e-3

        system.delete()

    def test_exchange_cubicanisotropy(self):
        name = 'hm_exchange_cubicanisotropy'
        if os.path.exists(name):
            shutil.rmtree(name)

        A = {'r1': 1e-12, 'r2': 0}
        K1 = 1e5
        u1 = (1, 0, 0)
        u2 = (0, 1, 0)
        Ms = 1e6

        mesh = oc.Mesh(p1=self.p1, p2=self.p2, cell=self.cell,
                       regions=self.regions)

        system = oc.System(name=name)
        system.hamiltonian = oc.Exchange(A=A) + \
            oc.CubicAnisotropy(K1=K1, u1=u1, u2=u2)
        system.m = df.Field(mesh, dim=3, value=(1, 0.3, 0), norm=Ms)

        md = oc.MinDriver()
        md.drive(system)

        value = system.m(mesh.random_point())
        assert np.linalg.norm(np.subtract(value, (Ms, 0, 0))) < 1e-3

        system.delete()

    def test_exchange_dmi_zeeman(self):
        name = 'hm_exchange_dmi_zeeman'
        if os.path.exists(name):
            shutil.rmtree(name)

        mesh = oc.Mesh(p1=self.p1, p2=self.p2, cell=self.cell,
                       regions=self.regions)

        # Very weak DMI and strong Zeeman to make the final
        # magnetisation uniform.
        A = {'r1': 1e-12, 'r2': 3e-12, 'r1:r2': 2e-12}
        D = {'r1': 1e-9, 'r2': 0, 'r1:r2': 5e-9}
        H = df.Field(mesh, dim=3, value=(1e10, 0, 0))
        Ms = 1e6

        system = oc.System(name=name)
        system.hamiltonian = oc.Exchange(A=A) + \
            oc.DMI(D=D, crystalclass='Cnv') + \
            oc.Zeeman(H=H)
        system.m = df.Field(mesh, dim=3, value=(1, 0.3, 0), norm=Ms)

        md = oc.MinDriver()
        md.drive(system)

        value = system.m(mesh.random_point())
        assert np.linalg.norm(np.subtract(value, (Ms, 0, 0))) < 1

        system.delete()

    def test_exchange_dmi_zeeman_uniaxialanisotropy_demag(self):
        name = 'exchange_dmi_zeeman_uniaxialanisotropy'
        if os.path.exists(name):
            shutil.rmtree(name)

        mesh = oc.Mesh(p1=self.p1, p2=self.p2, cell=self.cell,
                       regions=self.regions)

        # Very weak DMI and strong Zeeman to make the final
        # magnetisation uniform.
        A = {'r1': 1e-12, 'r2': 3e-12, 'r1:r2': 2e-12}
        D = {'r1': 1e-9, 'r2': 0, 'r1:r2': 5e-9}  # Very weak DMI
        H = df.Field(mesh, dim=3, value=(1e12, 0, 0))
        K1 = 1e6
        u = (1, 0, 0)
        Ms = 1e5

        system = oc.System(name=name)
        system.hamiltonian = oc.Exchange(A=A) + \
            oc.DMI(D=D, crystalclass='Cnv') + \
            oc.UniaxialAnisotropy(K1=K1, u=u) + \
            oc.Zeeman(H=H) + \
            oc.Demag()
        system.m = df.Field(mesh, dim=3, value=(1, 0.3, 0), norm=Ms)

        md = oc.MinDriver()
        md.drive(system)

        value = system.m(mesh.random_point())
        assert np.linalg.norm(np.subtract(value, (Ms, 0, 0))) < 1

        system.delete()
