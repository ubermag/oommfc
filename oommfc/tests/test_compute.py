import os
import sys
import shutil
import pytest
import oommfc as oc
import discretisedfield as df
import micromagneticmodel as mm


class TestCompute:
    def setup(self):
        name = 'compute_tests'
        if os.path.exists(name):
            shutil.rmtree(name)

        p1 = (0, 0, 0)
        p2 = (10e-9, 2e-9, 2e-9)
        cell = (2e-9, 2e-9, 2e-9)
        region = df.Region(p1=p1, p2=p2)
        mesh = df.Mesh(region=region, cell=cell)

        self.system = mm.System(name=name)
        self.system.energy = (mm.Exchange(A=1e-12) +
                              mm.Demag() +
                              mm.Zeeman(H=(8e6, 0, 0)) +
                              mm.UniaxialAnisotropy(K=1e4, u=(0, 0, 1)) +
                              mm.CubicAnisotropy(K=1e3, u1=(1, 0, 0),
                                                 u2=(0, 1, 0)))

        self.system.m = df.Field(mesh, dim=3, value=(0, 0, 1), norm=8e6)

    def test_energy(self):
        for term in self.system.energy:
            assert isinstance(oc.compute(term, 'energy', self.system), float)

        if os.path.exists(self.system.name):
            shutil.rmtree(self.system.name)

    def test_energy_density(self):
        for term in self.system.energy:
            assert isinstance(oc.compute(term, 'energy_density', self.system),
                              df.Field)

        if os.path.exists(self.system.name):
            shutil.rmtree(self.system.name)

    def test_effective_field(self):
        for term in self.system.energy:
            assert isinstance(oc.compute(term, 'effective_field', self.system),
                              df.Field)

        if os.path.exists(self.system.name):
            shutil.rmtree(self.system.name)

    def test_dmi(self):
        if sys.platform != 'win32':
            self.system.energy += mm.DMI(D=5e-3, crystalclass='T')
            term = self.system.energy.dmi
            for crystalclass in ['T', 'Cnv', 'D2d']:
                term.crystalclass = crystalclass
                assert isinstance(oc.compute(term, 'energy', self.system),
                                  float)
                assert isinstance(oc.compute(term, 'energy_density',
                                             self.system),
                                  df.Field)
                assert isinstance(oc.compute(term, 'effective_field',
                                             self.system),
                                  df.Field)

            if os.path.exists(self.system.name):
                shutil.rmtree(self.system.name)
