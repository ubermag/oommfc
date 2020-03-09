import sys
import random
import pytest
import numpy as np
import oommfc as oc
import discretisedfield as df
import micromagneticmodel as mm


class TestDMI:
    def setup(self):
        p1 = (-100e-9, 0, 0)
        p2 = (100e-9, 1e-9, 1e-9)
        self.region = df.Region(p1=p1, p2=p2)
        self.cell = (1e-9, 1e-9, 1e-9)
        self.subregions = {'r1': df.Region(p1=(-100e-9, 0, 0),
                                           p2=(0, 1e-9, 1e-9)),
                           'r2': df.Region(p1=(0, 0, 0),
                                           p2=(100e-9, 1e-9, 1e-9))}

    def random_m(self, pos):
        return [2*random.random()-1 for i in range(3)]

    def test_scalar(self):
        name = 'dmi_scalar'

        D = 1e-3
        Ms = 1e6

        system = mm.System(name=name)
        system.energy = mm.DMI(D=D, crystalclass='Cnv')

        mesh = df.Mesh(region=self.region, cell=self.cell)
        system.m = df.Field(mesh, dim=3, value=self.random_m, norm=Ms)

        md = oc.MinDriver()
        md.drive(system)

        # There are 4N cells in the mesh. Because of that the average should be
        # 0.
        assert np.linalg.norm(system.m.average) < 1

    def test_dict(self):
        name = 'dmi_dict'

        D = {'r1': 0, 'r2': 1e-3, 'default': 2e-3}
        Ms = 1e6

        system = mm.System(name=name)
        system.energy = mm.DMI(D=D, crystalclass='Cnv')

        mesh = df.Mesh(region=self.region, cell=self.cell,
                       subregions=self.subregions)
        system.m = df.Field(mesh, dim=3, value=self.random_m, norm=Ms)

        md = oc.MinDriver()
        md.drive(system)

        assert np.linalg.norm(system.m['r1'].average) > 1
        # There are 4N cells in the region with D!=0. Because of that
        # the average should be 0.
        assert np.linalg.norm(system.m['r2'].average) < 1

    @pytest.mark.skipif(sys.platform == 'win32',
                        reason=('Different crystalclasses are not '
                                'available on Windows.'))
    def test_crystalclass(self):
        name = 'dmi_crystalclass'

        D = 1e-3
        Ms = 1e6

        mesh = df.Mesh(region=self.region, cell=self.cell)

        for crystalclass in ['Cnv', 'T', 'O', 'D2d']:
            system = mm.System(name=name)
            system.energy = mm.DMI(D=D, crystalclass=crystalclass)

            system.m = df.Field(mesh, dim=3, value=self.random_m, norm=Ms)

            md = oc.MinDriver()
            md.drive(system)

            # There are 4N cells in the mesh. Because of that the
            # average should be 0.
            assert np.linalg.norm(system.m.average) < 1
