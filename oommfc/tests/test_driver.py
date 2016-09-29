import os
import discretisedfield as df
import oommfc as oc


class TestDriver:
    def setup(self):
        self.system = oc.System(name='tds')
        mesh = oc.Mesh((0, 0, 0),
                       (100e-9, 100e-9, 10e-9),
                       (10e-9, 10e-9, 10e-9))
        self.system.mesh = mesh
        self.system.hamiltonian += oc.Exchange(1.5e-11)
        self.system.hamiltonian += oc.Demag()
        self.system.dynamics += oc.Precession(2.211e5)
        self.system.dynamics += oc.Damping(0.02)
        self.system.m = df.Field(mesh, value=(0, 1, 0),
                                 normalisedto=8e5)

    def test_makedir(self):
        driver = oc.Driver()
        driver._makedir(self.system)

        dirname = "{}/".format(self.system.name)
        assert os.path.exists(dirname)

        os.system("rm -r {}".format(dirname))

    def test_filenames(self):
        driver = oc.Driver()
        filenames = driver._filenames(self.system)

        assert len(filenames.keys()) == 3
        assert filenames["dirname"] == 'tds/'
        assert filenames["omffilename"] == 'tds/m0.omf'
        assert filenames["miffilename"] == 'tds/tds.mif'
