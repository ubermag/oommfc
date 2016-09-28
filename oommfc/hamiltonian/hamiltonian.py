import micromagneticmodel as mm


class Hamiltonian(mm.Hamiltonian):
    def script(self):
        mif = ""
        for term in self.terms:
            mif += term.script()
        return mif
