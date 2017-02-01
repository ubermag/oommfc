import micromagneticmodel as mm


class DMI(mm.DMI):
    @property
    def _script(self):
        mif = "# BulkDMI\n"
        mif += "Specify Oxs_BulkDMI6ngbr {\n"
        mif += "  D {}\n".format(self.D)
        mif += "}\n\n"

        return mif
