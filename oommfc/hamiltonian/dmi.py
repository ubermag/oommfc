import micromagneticmodel as mm


class DMI(mm.DMI):
    @property
    def _script(self):
        if self.kind == "bulk" or self.kind == "T":
            mif = "# Bulk DMI (T symmetry class)\n"
            mif += "Specify Oxs_DMI_T {\n"
        elif self.kind == "interfacial" or self.kind == "Cnv":
            mif = "# Interfacial DMI (C_nv symmetry class)\n"
            mif += "Specify Oxs_DMI_Cnv {\n"
        elif self.kind == "D2d":
            mif = "# D_2d symmetry class DMI\n"
            mif += "Specify Oxs_DMI_D2d {\n"
        mif += "  default_D {}\n".format(self.D)
        mif += "  atlas :atlas\n"
        mif += "  D {\n"
        mif += "    atlas atlas {}\n".format(self.D)
        mif += "  }\n"
        mif += "}\n\n"

        return mif
