import micromagneticmodel as mm


class UniaxialAnisotropy(mm.UniaxialAnisotropy):
    def script(self):
        mif = "# UniaxialAnisotropy\n"
        mif += "Specify Oxs_UniaxialAnisotropy {\n"
        mif += "  K1 {}\n".format(self.K)
        mif += "  axis {{{} {} {}}}\n".format(*self.u)
        mif += "}\n\n"

        return mif
