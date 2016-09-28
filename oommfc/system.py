import micromagneticmodel as mm


class System(mm.System):
    def script(self):
        mif = self.mesh.script()
        mif += self.hamiltonian.script()
        return mif
