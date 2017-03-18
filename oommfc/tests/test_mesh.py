import oommfc as oc
import discretisedfield.tests as dft


class TestMesh(dft.TestMesh):
    def test_get_mif(self):
        for p1, p2, cell in self.valid_args:
            name = "test_mesh"

            mesh = oc.Mesh(p1, p2, cell, name=name)

            script = mesh._script
            assert script.count("\n") == 14
            assert script[0] == "#"
            assert script[-1] == "\n"

            lines = script.split("\n")
            assert len(lines) == 15

            # Assert BoxAtlas script
            assert lines[0] == "# BoxAtlas"
            assert lines[1] == "Specify Oxs_BoxAtlas:atlas {"
            assert lines[2] == "  xrange {{{} {}}}".format(mesh.pmin[0],
                                                           mesh.pmax[0])
            assert lines[3] == "  yrange {{{} {}}}".format(mesh.pmin[1],
                                                           mesh.pmax[1])
            assert lines[4] == "  zrange {{{} {}}}".format(mesh.pmin[2],
                                                           mesh.pmax[2])
            assert lines[5] == "  name atlas"
            assert lines[6] == "}"

            # Empty line between BoxAtlas and RectangularMesh
            assert lines[7] == ""

            # Assert RectangularMesh script
            assert lines[8] == "# RectangularMesh"
            assert lines[9] == "Specify Oxs_RectangularMesh:{} {{".format(name)
            assert lines[10] == "  cellsize {{{} {} {}}}".format(*cell)
            assert lines[11] == "  atlas Oxs_BoxAtlas:atlas"
            assert lines[12] == "}"
