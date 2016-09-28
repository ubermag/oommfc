import micromagneticmodel as mm


class UniaxialAnisotropy(mm.UniaxialAnisotropy):
    def script(self):
        mif = "# UniaxialAnisotropy\n"
        mif += "Specify Oxs_UniaxialAnisotropy {\n"
        mif += "  K1 {}\n".format(self.K)
        mif += "  axis {{{} {} {}}}\n".format(self.u[0], self.u[1], self.u[2])
        mif += "}\n\n"

        return mif
