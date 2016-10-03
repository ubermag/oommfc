import textwrap
import discretisedfield as df


class Mesh(df.Mesh):
    def script(self):
        mif = "# BoxAtlas\n"
        mif += "Specify Oxs_BoxAtlas:atlas {\n"
        mif += "  xrange {{{} {}}}\n".format(self.p1[0], self.p2[0])
        mif += "  yrange {{{} {}}}\n".format(self.p1[1], self.p2[1])
        mif += "  zrange {{{} {}}}\n".format(self.p1[2], self.p2[2])
        mif += "}\n\n"
        mif += "# RectangularMesh\n"
        mif += "Specify Oxs_RectangularMesh:{} {{\n".format(self.name)
        mif += "  cellsize {{{} {} {}}}\n".format(self.cell[0],
                                                  self.cell[1],
                                                  self.cell[2])
        mif += "  atlas Oxs_BoxAtlas:atlas\n"
        mif += "}\n\n"

        return mif
