import micromagneticmodel as mm


class System(mm.System):
    @property
    def script(self):
        mif = self.m.mesh.script
        mif += self.hamiltonian.script
        return mif

    def total_energy(self):
        for key in self.dt.tail(1).keys():
            if "Totalenergy" in key:
                return self.dt.tail(1)[key][0]
