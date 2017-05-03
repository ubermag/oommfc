import micromagneticmodel as mm


class UniaxialAnisotropy(mm.UniaxialAnisotropy):
    @property
    def _script(self):
        mif = "# UniaxialAnisotropy\n"
        if self.K2 == 0:
            mif += "Specify Oxs_UniaxialAnisotropy {\n"
            mif += "  K1 {}\n".format(self.K1)
            mif += "  axis {{{} {} {}}}\n".format(*self.u)
            mif += "}\n\n"
        else:
            mif += "Specify Southampton_UniaxialAnisotropy4 {\n"
            mif += "  K1 {}\n".format(self.K1)
            mif += "  K2 {}\n".format(self.K2)
            mif += "  axis {{{} {} {}}}\n".format(*self.u)
            mif += "}\n\n"

        return mif
