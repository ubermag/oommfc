import micromagneticmodel as mm


class System(mm.System):
    def script(self):
        mif = self.mesh.script()
        mif += self.hamiltonian.script()
        return mif

    def total_energy(self):
        for key in self.dt.tail(1).keys():
            if "Totalenergy" in key:
                return self.dt.tail(1)[key][0]
