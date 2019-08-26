import os
import sys
import shutil
import random
import numpy as np
import oommfc as oc
import discretisedfield as df


class TestDMI:
    def setup(self):
        self.p1 = (-100e-9, 0, 0)
        self.p2 = (100e-9, 1e-9, 1e-9)
        self.cell = (1e-9, 1e-9, 1e-9)
        self.regions = {'r1': df.Region(p1=(-100e-9, 0, 0),
                                        p2=(0, 1e-9, 1e-9)),
                        'r2': df.Region(p1=(0, 0, 0),
                                        p2=(100e-9, 1e-9, 1e-9))}

    def test_scalar(self):
        name = 'dm_scalar'
        if os.path.exists(name):
            shutil.rmtree(name)

        D = 1e-3
        Ms = 1e6

        mesh = oc.Mesh(p1=self.p1, p2=self.p2, cell=self.cell)

        system = oc.System(name=name)
        system.hamiltonian = oc.DMI(D=D, crystalclass='Cnv')

        def m_value(pos):
            return [2*random.random()-1 for i in range(3)]

        system.m = df.Field(mesh, dim=3, value=m_value, norm=Ms)

        md = oc.MinDriver()
        md.drive(system)

        # There are 4N cells in the mesh. Because of that the average
        # should be 0.
        assert np.linalg.norm(system.m.average) < 1

        system.delete()

    def test_dict(self):
        name = 'dm_dict'
        if os.path.exists(name):
            shutil.rmtree(name)

        D = {'r1': 0, 'r2': 1e-3}
        Ms = 1e6

        mesh = oc.Mesh(p1=self.p1, p2=self.p2, cell=self.cell,
                       regions=self.regions)

        system = oc.System(name=name)
        system.hamiltonian = oc.DMI(D=D, crystalclass='Cnv')

        def m_value(pos):
            return [2*random.random()-1 for i in range(3)]

        system.m = df.Field(mesh, dim=3, value=m_value, norm=Ms)

        md = oc.MinDriver()
        md.drive(system)

        r1_mesh = df.Mesh(p1=self.regions['r1'].pmin,
                          p2=self.regions['r1'].pmax,
                          cell=self.cell)
        r2_mesh = df.Mesh(p1=self.regions['r2'].pmin,
                          p2=self.regions['r2'].pmax,
                          cell=self.cell)
        r1_field = df.Field(r1_mesh, dim=3, value=system.m)
        r2_field = df.Field(r2_mesh, dim=3, value=system.m)

        assert np.linalg.norm(r1_field.average) > 1
        # There are 4N cells in the region with D!=0. Because of that
        # the average should be 0.
        assert np.linalg.norm(r2_field.average) < 1

        system.delete()

    def test_crystalclass(self):
        name = 'dm_crystalclass'

        D = 1e-3
        Ms = 1e6

        mesh = oc.Mesh(p1=self.p1, p2=self.p2, cell=self.cell)

        def m_value(pos):
            return [2*random.random()-1 for i in range(3)]

        for crystalclass in ['Cnv', 'T', 'O', 'D2d']:
            if crystalclass != 'Cnv' and sys.platform == 'win32':
                pass
            else:
                if os.path.exists(name):
                    shutil.rmtree(name)

                system = oc.System(name=name)
                system.hamiltonian = oc.DMI(D=D, crystalclass=crystalclass)

                system.m = df.Field(mesh, dim=3, value=m_value, norm=Ms)

                md = oc.MinDriver()
                md.drive(system)

                # There are 4N cells in the mesh. Because of that the
                # average should be 0.
                assert np.linalg.norm(system.m.average) < 1

                system.delete()
