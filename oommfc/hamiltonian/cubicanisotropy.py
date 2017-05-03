import micromagneticmodel as mm


class CubicAnisotropy(mm.CubicAnisotropy):
    @property
    def _script(self):
        mif = "# CubicAnisotropy\n"
        mif += "Specify Oxs_CubicAnisotropy {\n"
        mif += "  K1 {}\n".format(self.K1)
        mif += "  axis1 {{{} {} {}}}\n".format(*self.u1)
        mif += "  axis2 {{{} {} {}}}\n".format(*self.u2)
        mif += "}\n\n"

        return mif
