import os
import glob
import pytest
import oommfc as oc
import numpy as np
import discretisedfield as df
import micromagneticmodel as mm


class TestMinDriver:
    def setup(self):
        p1 = (0, 0, 0)
        p2 = (5e-9, 5e-9, 5e-9)
        n = (5, 5, 5)
        self.Ms = 1e6
        A = 1e-12
        H = (0, 0, 1e6)
        region = df.Region(p1=p1, p2=p2)
        self.mesh = df.Mesh(region=region, n=n)
        self.energy = mm.Exchange(A=A) + mm.Zeeman(H=H)
        self.m = df.Field(self.mesh, dim=3, value=(0, 1, 0), norm=self.Ms)

    def test_noevolver_nodriver(self):
        name = 'mindriver_noevolver_nodriver'

        system = mm.System(name=name)
        system.energy = self.energy
        system.m = self.m

        md = oc.MinDriver()
        md.drive(system)

        value = system.m(self.mesh.region.random_point())
        assert np.linalg.norm(np.subtract(value, (0, 0, self.Ms))) < 1e-3

    def test_evolver_nodriver(self):
        name = 'mindriver_evolver_nodriver'

        system = mm.System(name=name)
        system.energy = self.energy
        system.m = self.m

        evolver = oc.CGEvolver(method='Polak-Ribiere')
        md = oc.MinDriver(evolver=evolver)
        md.drive(system)

        value = system.m(self.mesh.region.random_point())
        assert np.linalg.norm(np.subtract(value, (0, 0, self.Ms))) < 1e-3

    def test_noevolver_driver(self):
        name = 'mindriver_noevolver_driver'

        system = mm.System(name=name)
        system.energy = self.energy
        system.m = self.m

        md = oc.MinDriver(stopping_mxHxm=0.1)
        md.drive(system)

        value = system.m(self.mesh.region.random_point())
        assert np.linalg.norm(np.subtract(value, (0, 0, self.Ms))) < 1e-3

    def test_evolver_driver(self):
        name = 'mindriver_evolver_driver'

        system = mm.System(name=name)
        system.energy = self.energy
        system.m = self.m

        evolver = oc.CGEvolver(method='Polak-Ribiere')
        md = oc.MinDriver(evolver=evolver, stopping_mxHxm=0.1)
        md.drive(system)

        value = system.m(self.mesh.region.random_point())
        assert np.linalg.norm(np.subtract(value, (0, 0, self.Ms))) < 1e-3

    def test_output_files(self):
        name = 'mindriver_output_files'

        system = mm.System(name=name)
        system.energy = self.energy
        system.m = self.m

        md = oc.MinDriver()
        md.drive(system, save=True, overwrite=True)

        dirname = os.path.join(f'{name}', f'drive-{system.drive_number-1}')
        assert os.path.exists(dirname)
        miffilename = os.path.join(dirname, f'{name}.mif')
        assert os.path.isfile(miffilename)
        omf_files = list(glob.iglob(os.path.join(dirname, '*.omf')))
        assert len(omf_files) == 2
        odt_files = list(glob.iglob(os.path.join(dirname, '*.odt')))
        assert len(odt_files) == 1
        omffilename = os.path.join(dirname, 'm0.omf')
        assert omffilename in omf_files

        oc.delete(system)

    def test_wrong_evolver(self):
        system = mm.examples.macrospin()
        evolver = oc.RungeKuttaEvolver()
        md = oc.MinDriver(evolver=evolver)

        with pytest.raises(TypeError):
            md.drive(system)
