import micromagneticmodel as mm


class DMI(mm.DMI):
    @property
    def _script(self):
        if self.kind == "bulk":
            mif = "# BulkDMI\n"
            mif += "Specify Oxs_BulkDMI {\n"
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
