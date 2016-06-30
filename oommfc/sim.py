import os
import glob
from .atlases import BoxAtlas
from .meshes import RectangularMesh
from .evolvers import RungeKuttaEvolve, CGEvolve
from .drivers import TimeDriver, MinDriver
from oommffield import Field, read_oommf_file
from oommfc.energies.zeeman import FixedZeeman
from oommfodt import OOMMFodt


class Sim(object):
    def __init__(self, mesh, Ms, name=None):
        self.mesh = mesh
        self.atlas = mesh.atlas
        self.Ms = Ms
        self.name = name

        self.energies = []

        # Set default alpha value.
        self.alpha = 1

        self.dirname = self.name + '/'
        if not os.path.exists(self.dirname):
            os.makedirs(self.dirname)
        self.mif_filename = self.dirname + self.name + '.mif'

        self.m =  Field(self.atlas.cmin, self.atlas.cmax, self.mesh.d, dim=3)

        self.t = 0

    def add(self, energy):
        self.energies.append(energy)

    def set_H(self, H):
        for energy in self.energies:
            if isinstance(energy, FixedZeeman):
                self.energies.remove(energy)
        zeeman = FixedZeeman(H)
        self.add(zeeman)

    def run_until(self, stopping_time, stages=1):
        self.m.write_oommf_file(self.dirname + 'm0file.omf')
        self.m0 = 'm0file.omf'

        self.evolver = RungeKuttaEvolve(self.alpha)
        self.driver = TimeDriver('evolver', stopping_time/stages, stages,
                                 'mesh', self.Ms, self.m0, basename=self.name)
        self.relaxation = False
        self.execute_mif()
        self.t += stopping_time

    def m_average(self):
        return self.m.average()

    def relax(self, stopping_mxHxm=0.01):
        self.m.write_oommf_file(self.dirname + 'm0file.omf')
        self.m0 = 'm0file.omf'

        self.evolver = CGEvolve()
        self.driver = MinDriver('evolver', stopping_mxHxm, 'mesh',
                                self.Ms, self.m0, basename=self.name)
        self.relaxation = True
        self.execute_mif()

    def set_m(self, m0):
        if isinstance(m0, (list, tuple)):
            self.m.set(m0)
        elif isinstance(m0, str):
            self.m = read_oommf_file(m0)
        elif hasattr(m0, '__call__'):
            self.m.set(m0)
        elif isinstance(m0, Field):
            self.m = m0
            self.m.write_oommf_file(self.dirname + 'm0file.omf')
        else:
            raise ValueError('m0 type invalid.')

    def get_mif(self):
        mif = '# MIF 2.1\n\n'
        mif += self.atlas.get_mif()
        mif += self.mesh.get_mif()
        for i in self.energies:
            mif += i.get_mif()
        mif += self.evolver.get_mif()
        mif += self.driver.get_mif()
        mif += 'Destination table mmArchive\n'
        mif += 'Destination mags mmArchive\n\n'
        mif += 'Schedule DataTable table Stage 1\n'
        if self.relaxation:
            mif += 'Schedule Oxs_MinDriver::Spin mags Stage 1'
        else:
            mif += 'Schedule Oxs_TimeDriver::Spin mags Stage 1'

        return mif

    def create_mif(self):
        miffile = open(self.mif_filename, 'w')
        miffile.write(self.get_mif())
        miffile.close()

    def last_omf_file(self):
        newest_omf = max(glob.iglob(self.dirname+'*.omf'), key=os.path.getctime)
        return newest_omf

    def last_odt_file(self):
        newest_odt = max(glob.iglob(self.dirname+'*.odt'), key=os.path.getctime)
        return newest_odt

    def update_self(self):
        newest_omf = self.last_omf_file()
        self.m = read_oommf_file(newest_omf)

        newest_odt = self.last_odt_file()
        self.odt_file = OOMMFodt(newest_odt)
        self.data = self.odt_file.last_row()

    def total_energy(self):
        return self.data['E']

    def execute_mif(self):
        self.create_mif()

        oommf_command = 'tclsh $OOMMFTCL boxsi +fg '
        oommf_command += self.mif_filename
        oommf_command += ' -exitondone 1'
        os.system('cd ' + self.dirname)
        os.system(oommf_command)

        self.update_self()
