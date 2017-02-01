import textwrap
import discretisedfield as df


class Mesh(df.Mesh):
    @property
    def _script(self):
        mif = "# BoxAtlas\n"
        mif += "Specify Oxs_BoxAtlas:atlas {\n"
        mif += "  xrange {{{} {}}}\n".format(self.pmin[0], self.pmax[0])
        mif += "  yrange {{{} {}}}\n".format(self.pmin[1], self.pmax[1])
        mif += "  zrange {{{} {}}}\n".format(self.pmin[2], self.pmax[2])
        mif += "  name atlas\n"
        mif += "}\n\n"
        mif += "# RectangularMesh\n"
        mif += "Specify Oxs_RectangularMesh:{} {{\n".format(self.name)
        mif += "  cellsize {{{} {} {}}}\n".format(*self.cell)
        mif += "  atlas Oxs_BoxAtlas:atlas\n"
        mif += "}\n\n"

        return mif
