import os
import shutil
import micromagneticmodel as mm


class System(mm.System):
    @property
    def _script(self):
        mif = self.m.mesh._script
        mif += self.hamiltonian._script

        return mif

    def total_energy(self):
        return self.dt.tail(1)['E'][0]

    def delete(self):
        if os.path.exists(f'{self.name}'):
            shutil.rmtree(self.name)
