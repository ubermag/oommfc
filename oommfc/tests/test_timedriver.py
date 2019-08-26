import os
import glob
import shutil
import pytest
import oommfc as oc
import numpy as np
import discretisedfield as df


class TestTimeDriver:
    def setup(self):
        p1 = (0, 0, 0)
        p2 = (5e-9, 5e-9, 5e-9)
        n = (2, 2, 2)
        self.Ms = 1e6
        A = 1e-12
        H = (0, 0, 1e6)
        self.mesh = oc.Mesh(p1=p1, p2=p2, n=n)
        self.hamiltonian = oc.Exchange(A=A) + oc.Zeeman(H=H)
        self.precession = oc.Precession(gamma=oc.consts.gamma0)
        self.damping = oc.Damping(alpha=1)
        self.m = df.Field(self.mesh, dim=3, value=(0, 0.1, 1), norm=self.Ms)

    def test_noevolver_nodriver(self):
        name = 'td_noevolver_nodriver'
        if os.path.exists(name):
            shutil.rmtree(name)

        system = oc.System(name=name)
        system.hamiltonian = self.hamiltonian
        system.dynamics = self.precession + self.damping
        system.m = self.m

        td = oc.TimeDriver()
        td.drive(system, t=0.2e-9, n=50)

        value = system.m(self.mesh.random_point())
        assert np.linalg.norm(np.subtract(value, (0, 0, self.Ms))) < 1

        system.delete()

    def test_rungekutta_evolver_nodriver(self):
        name = 'td_rungekutta_evolver_nodriver'
        if os.path.exists(name):
            shutil.rmtree(name)

        system = oc.System(name=name)
        system.hamiltonian = self.hamiltonian
        system.dynamics = self.precession + self.damping
        system.m = self.m

        evolver = oc.RungeKuttaEvolver(method='rkf54s')
        td = oc.TimeDriver(evolver=evolver)
        td.drive(system, t=0.2e-9, n=50)

        value = system.m(self.mesh.random_point())
        assert np.linalg.norm(np.subtract(value, (0, 0, self.Ms))) < 1

        system.delete()

    def test_euler_evolver_nodriver(self):
        name = 'td_euler_evolver_nodriver'
        if os.path.exists(name):
            shutil.rmtree(name)

        system = oc.System(name=name)
        system.hamiltonian = self.hamiltonian
        system.dynamics = self.precession + self.damping
        system.m = self.m

        evolver = oc.EulerEvolver(start_dm=0.02)
        td = oc.TimeDriver(evolver=evolver)
        td.drive(system, t=0.2e-9, n=50)

        value = system.m(self.mesh.random_point())
        assert np.linalg.norm(np.subtract(value, (0, 0, self.Ms))) < 1

        system.delete()

    def test_noevolver_driver(self):
        name = 'td_noevolver_driver'
        if os.path.exists(name):
            shutil.rmtree(name)

        system = oc.System(name=name)
        system.hamiltonian = self.hamiltonian
        system.dynamics = self.precession + self.damping
        system.m = self.m

        td = oc.TimeDriver(stopping_dm_dt=0.01)
        td.drive(system, t=0.3e-9, n=50)

        value = system.m(self.mesh.random_point())
        assert np.linalg.norm(np.subtract(value, (0, 0, self.Ms))) < 1

        system.delete()

    def test_noprecession(self):
        name = 'td_noprecession'
        if os.path.exists(name):
            shutil.rmtree(name)

        system = oc.System(name=name)
        system.hamiltonian = self.hamiltonian
        system.dynamics = self.damping
        system.m = self.m

        td = oc.TimeDriver()
        td.drive(system, t=0.2e-9, n=50)

        value = system.m(self.mesh.random_point())
        assert np.linalg.norm(np.subtract(value, (0, 0, self.Ms))) < 1

        system.delete()

    def test_nodamping(self):
        name = 'td_nodamping'
        if os.path.exists(name):
            shutil.rmtree(name)

        system = oc.System(name=name)
        system.hamiltonian = self.hamiltonian
        system.dynamics = self.precession
        system.m = self.m

        td = oc.TimeDriver()
        td.drive(system, t=0.2e-9, n=50)

        value = system.m(self.mesh.random_point())
        assert np.linalg.norm(np.subtract(value, (0, 0, self.Ms))) > 1e3

        system.delete()

    def test_output_files(self):
        name = 'td_output_files'
        if os.path.exists(name):
            shutil.rmtree(name)

        system = oc.System(name=name)
        system.hamiltonian = self.hamiltonian
        system.dynamics = self.precession + self.damping
        system.m = self.m

        td = oc.TimeDriver()
        td.drive(system, t=0.2e-9, n=50)

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

        system.delete()

    def test_drive_exception(self):
        name = 'td_exception'
        if os.path.exists(name):
            shutil.rmtree(name)

        system = oc.System(name=name)
        system.hamiltonian = self.hamiltonian
        system.dynamics = self.precession + self.damping
        system.m = self.m

        td = oc.TimeDriver()
        with pytest.raises(ValueError):
            td.drive(system, t=-0.1e-9, n=10)
        with pytest.raises(ValueError):
            td.drive(system, t=0.1e-9, n=-10)

        system.delete()
