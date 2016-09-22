from micromagneticmodel.hamiltonian import Exchange


class Exchange(Exchange):
    def script(self):
        mif = "# UniformExchange\n"
        mif += "Specify Oxs_UniformExchange {\n"
        mif += "  A {}\n".format(self.A)
        mif += "}\n\n"

        return mif
