import micromagneticmodel.hamiltonian as hamil


class Hamiltonian(hamil.Hamiltonian):
    def script(self):
        mif = ""
        for term in self.terms:
            mif += term.script()
        return mif
