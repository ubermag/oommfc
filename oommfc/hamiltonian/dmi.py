import micromagneticmodel as mm


class DMI(mm.DMI):
    @property
    def _script(self):
        if self.crystalclass in ["t", "o"]:
            mif = "# DMI of crystallographic class T(O)\n"
            mif += "Specify Oxs_DMI_T {\n"
        elif self.crystalclass == "cnv":
            mif = "# DMI of crystallographic class Cnv\n"
            mif += "Specify Oxs_DMI_Cnv {\n"
        elif self.crystalclass == "d2d":
            mif = "# DMI of crystallographic class D2d\n"
            mif += "Specify Oxs_DMI_D2d {\n"
        elif self.kind == "interfacial":
            mif = "# InterfacialDMI\n"
            mif += "Specify Oxs_DMExchange6Ngbr {\n"
        mif += "  default_D {}\n".format(self.D)
        mif += "  atlas :atlas\n"
        mif += "  D {\n"
        mif += "    atlas atlas {}\n".format(self.D)
        mif += "  }\n"
        mif += "}\n\n"

        return mif
