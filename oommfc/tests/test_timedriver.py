import os
import glob
import pytest
import numpy as np
import oommfc as oc
import discretisedfield as df
import micromagneticmodel as mm


class TestTimeDriver:
    def setup(self):
        p1 = (0, 0, 0)
        p2 = (5e-9, 5e-9, 5e-9)
        n = (2, 2, 2)
        self.Ms = 1e6
        A = 1e-12
        H = (0, 0, 1e6)
        region = df.Region(p1=p1, p2=p2)
        self.mesh = df.Mesh(region=region, n=n)
        self.energy = mm.Exchange(A=A) + mm.Zeeman(H=H)
        self.precession = mm.Precession(gamma0=mm.consts.gamma0)
        self.damping = mm.Damping(alpha=1)
        self.m = df.Field(self.mesh, dim=3, value=(0, 0.1, 1), norm=self.Ms)

    def test_noevolver_nodriver(self):
        name = 'timedriver_noevolver_nodriver'

        system = mm.System(name=name)
        system.energy = self.energy
        system.dynamics = self.precession + self.damping
        system.m = self.m

        td = oc.TimeDriver()
        td.drive(system, t=0.2e-9, n=50)

        value = system.m(self.mesh.region.random_point())
        assert np.linalg.norm(np.subtract(value, (0, 0, self.Ms))) < 1

    def test_rungekutta_evolver_nodriver(self):
        name = 'timedriver_rungekutta_evolver_nodriver'

        system = mm.System(name=name)
        system.energy = self.energy
        system.dynamics = self.precession + self.damping
        system.m = self.m

        evolver = oc.RungeKuttaEvolver(method='rkf54s')
        td = oc.TimeDriver(evolver=evolver)
        td.drive(system, t=0.2e-9, n=50)

        value = system.m(self.mesh.region.random_point())
        assert np.linalg.norm(np.subtract(value, (0, 0, self.Ms))) < 1

    def test_euler_evolver_nodriver(self):
        name = 'timedriver_euler_evolver_nodriver'

        system = mm.System(name=name)
        system.energy = self.energy
        system.dynamics = self.precession + self.damping
        system.m = self.m

        evolver = oc.EulerEvolver(start_dm=0.02)
        td = oc.TimeDriver(evolver=evolver)
        td.drive(system, t=0.2e-9, n=50)

        value = system.m(self.mesh.region.random_point())
        assert np.linalg.norm(np.subtract(value, (0, 0, self.Ms))) < 1

    def test_noevolver_driver(self):
        name = 'timedriver_noevolver_driver'

        system = mm.System(name=name)
        system.energy = self.energy
        system.dynamics = self.precession + self.damping
        system.m = self.m

        td = oc.TimeDriver(stopping_dm_dt=0.01)
        td.drive(system, t=0.3e-9, n=50)

        value = system.m(self.mesh.region.random_point())
        assert np.linalg.norm(np.subtract(value, (0, 0, self.Ms))) < 1

    def test_noprecession(self):
        name = 'timedriver_noprecession'

        system = mm.System(name=name)
        system.energy = self.energy
        system.dynamics = self.damping
        system.m = self.m

        td = oc.TimeDriver()
        td.drive(system, t=0.2e-9, n=50)

        value = system.m(self.mesh.region.random_point())
        assert np.linalg.norm(np.subtract(value, (0, 0, self.Ms))) < 1

    def test_nodamping(self):
        name = 'timedriver_nodamping'

        system = mm.System(name=name)
        system.energy = self.energy
        system.dynamics = self.precession
        system.m = self.m

        td = oc.TimeDriver()
        td.drive(system, t=0.2e-9, n=50)

        value = system.m(self.mesh.region.random_point())
        assert np.linalg.norm(np.subtract(value, (0, 0, self.Ms))) > 1e3

    def test_output_files(self):
        name = 'timedriver_output_files'

        system = mm.System(name=name)
        system.energy = self.energy
        system.dynamics = self.precession + self.damping
        system.m = self.m

        td = oc.TimeDriver()
        td.drive(system, t=0.2e-9, n=50, save=True, overwrite=True)

        dirname = os.path.join(f'{name}', f'drive-{system.drive_number-1}')
        assert os.path.exists(dirname)
        miffilename = os.path.join(dirname, f'{name}.mif')
        assert os.path.isfile(miffilename)
        omf_files = list(glob.iglob(os.path.join(dirname, '*.omf')))
        assert len(omf_files) == 51
        odt_files = list(glob.iglob(os.path.join(dirname, '*.odt')))
        assert len(odt_files) == 1
        omffilename = os.path.join(dirname, 'm0.omf')
        assert omffilename in omf_files

        oc.delete(system)

    def test_drive_exception(self):
        name = 'timedriver_exception'

        system = mm.System(name=name)
        system.energy = self.energy
        system.dynamics = self.precession + self.damping
        system.m = self.m

        td = oc.TimeDriver()
        with pytest.raises(ValueError):
            td.drive(system, t=-0.1e-9, n=10)
        with pytest.raises(ValueError):
            td.drive(system, t=0.1e-9, n=-10)

    def test_wrong_evolver(self):
        system = mm.examples.macrospin()
        evolver = oc.CGEvolver()
        td = oc.TimeDriver(evolver=evolver)

        with pytest.raises(TypeError):
            td.drive(system, t=1e-12, n=1)
