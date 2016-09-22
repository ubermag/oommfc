from micromagneticmodel.hamiltonian import Hamiltonian


class Hamiltonian(Hamiltonian):
    def script(self):
        mif = ""
        for term in self.terms:
            mif += term.script()

        return mif
