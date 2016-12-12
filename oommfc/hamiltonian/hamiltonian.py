import micromagneticmodel as mm


class Hamiltonian(mm.Hamiltonian):
    @property
    def script(self):
        mif = ""
        for term in self.terms:
            mif += term.script
        return mif
