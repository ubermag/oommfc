import oommfc as oc
import discretisedfield.tests as dft


class TestMesh(dft.TestMesh):
    def test_get_mif(self):
        for arg in self.valid_args:
            p1 = arg[0]
            p2 = arg[1]
            cell = arg[2]
            name = "test_mesh"

            mesh = oc.Mesh(p1, p2, cell, name=name)

            script = mesh.script()
            assert script.count("\n") == 13
            assert script[0] == "#"
            assert script[-1] == "\n"

            lines = script.split("\n")
            assert len(lines) == 14

            # Assert BoxAtlas script
            assert lines[0] == "# BoxAtlas"
            assert lines[1] == "Specify Oxs_BoxAtlas:atlas {"
            assert lines[2] == "  xrange {{{} {}}}".format(p1[0], p2[0])
            assert lines[3] == "  yrange {{{} {}}}".format(p1[1], p2[1])
            assert lines[4] == "  zrange {{{} {}}}".format(p1[2], p2[2])
            assert lines[5] == "}"

            # Empty line between BoxAtlas and RectangularMesh
            assert lines[6] == ""

            # Assert RectangularMesh script
            assert lines[7] == "# RectangularMesh"
            assert lines[8] == "Specify Oxs_RectangularMesh:{} {{".format(name)
            assert lines[9] == "  cellsize {{{} {} {}}}".format(cell[0],
                                                                cell[1],
                                                                cell[2])
            assert lines[10] == "  atlas Oxs_BoxAtlas:atlas"
            assert lines[11] == "}"
