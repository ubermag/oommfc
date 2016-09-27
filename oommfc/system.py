from micromagneticmodel import System


class System(System):
    def script(self):
        mif = self.mesh.script()
        mif += self.hamiltonian.script()
        return mif
