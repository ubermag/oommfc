from micromagneticmodel.hamiltonian import Demag


class Demag(Demag):
    def script(self):
        mif = "# Demag\n"
        mif += "Specify Oxs_Demag {}\n\n"

        return mif
