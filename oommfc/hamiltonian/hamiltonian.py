import micromagneticmodel as mm


class Hamiltonian(mm.Hamiltonian):
    @property
    def _script(self):
        mif = ""
        for term in self.terms:
            mif += term._script
        return mif
