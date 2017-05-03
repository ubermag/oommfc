import micromagneticmodel as mm


class UniaxialAnisotropy(mm.UniaxialAnisotropy):
    @property
    def _script(self):
        mif = "# UniaxialAnisotropy\n"
        mif += "Specify Oxs_UniaxialAnisotropy {\n"
        mif += "  K1 {}\n".format(self.K1)
        mif += "  axis {{{} {} {}}}\n".format(*self.u)
        mif += "}\n\n"

        return mif
