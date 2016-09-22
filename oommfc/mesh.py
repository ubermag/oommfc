import textwrap
import discretisedfield as df


class Mesh(df.Mesh):
    def script(self):
        mif = "# BoxAtlas\n"
        mif += "Specify Oxs_BoxAtlas:atlas {\n"
        mif += "  xrange {{{} {}}}\n".format(self.c1[0], self.c2[0])
        mif += "  yrange {{{} {}}}\n".format(self.c1[1], self.c2[1])
        mif += "  zrange {{{} {}}}\n".format(self.c1[2], self.c2[2])
        mif += "}\n\n"
        mif += "# RectangularMesh\n"
        mif += "Specify Oxs_RectangularMesh:{} {{\n".format(self.name)
        mif += "  cellsize {{{} {} {}}}\n".format(self.d[0],
                                                  self.d[1],
                                                  self.d[2])
        mif += "  atlas Oxs_BoxAtlas:atlas\n"
        mif += "}\n\n"

        return mif
