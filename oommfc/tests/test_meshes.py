import pytest
from oommfc import RectangularMesh
from oommfc import BoxAtlas


class TestRectangularMesh(object):
    def setup(self):
        # Set of valid arguments.
        atlas1 = BoxAtlas((0, 0, 0), (5, 5, 5), 'atlas1', 'rn1')
        atlas2 = BoxAtlas((0, 0, 0), (5e-9, 5e-9, 5e-9), 'atlas2', 'rn2')
        atlas3 = BoxAtlas((-1.5e-9, -5e-9, 0), (1.5e-9, 15e-9, 16e-9),
                          'atlas3', 'rn3')
        atlas4 = BoxAtlas((-1.5e-9, -5e-9, -5e-9), (0, 0, 0), 'atlas3', 'rn3')
        self.args1 = [[atlas1, (1, 1, 1), 'mesh1'],
                      [atlas2, (1e-9, 1e-9, 1e-9), 'mesh2'],
                      [atlas3, (5, 1, 1e-9), 'mesh3'],
                      [atlas4, (1.0, 13-6, 1.1e4), 'mesh4']]

        # Invalid arguments.
        self.args2 = [[atlas1, (-1, 1, 1), 'mesh1'],
                      ['1', (0, 0, 1e-9), 'mesh2'],
                      [atlas3, (5, 1, -1e-9), 'mesh3'],
                      [atlas4, (1.0, 13-6, 1.1e4), 52],
                      [atlas3, (-2e-9, 1, 1e-9), 'mesh3'],
                      ['atlas3', (5, 1, 1e-9), 'mesh3'],
                      [atlas3, 1, 'mesh3']]

    def test_init(self):
        # Valid arguments.
        for arg in self.args1:
            atlas = arg[0]
            d = arg[1]
            meshname = arg[2]

            mesh = RectangularMesh(atlas, d, meshname)

            assert mesh.atlas == atlas
            assert mesh.d == d
            assert mesh.meshname == meshname

            assert isinstance(mesh.atlas, BoxAtlas)
            assert isinstance(mesh.d, tuple)
            assert isinstance(mesh.meshname, str)

    def test_init_exceptions(self):
        # Invalid arguments (ValueError expected).
        for arg in self.args2:
            with pytest.raises(ValueError):
                atlas = arg[0]
                d = arg[1]
                meshname = arg[2]

                mesh = RectangularMesh(atlas, d, meshname)

    def test_get_mif(self):
        for arg in self.args1:
            atlas = arg[0]
            d = arg[1]
            meshname = arg[2]

            mesh = RectangularMesh(atlas, d, meshname)

            mif = mesh.get_mif()
            mif_lines = mesh.get_mif().split('\n')

            # Assert comment.
            l = mif_lines[0].split()
            assert l[0] == '#'
            assert l[1] == 'RectangularMesh'

            # Assert Specify line.
            l = mif_lines[1].split()
            assert l[0] == 'Specify'
            assert l[1].split(':')[0] == 'Oxs_RectangularMesh'
            assert l[1].split(':')[1] == meshname
            assert l[2] == '{'

            # Assert step line.
            assert mif_lines[2][0] == '\t'
            l = mif_lines[2].split()
            assert l[0] == 'cellsize'
            assert l[1] == '{'
            assert float(l[2]) == d[0]
            assert float(l[3]) == d[1]
            assert float(l[4]) == d[2]
            assert l[5] == '}'

            # Assert atlas name.
            assert mif_lines[3][0] == '\t'
            l = mif_lines[3].split()
            assert l[0] == 'atlas'
            assert l[1] == atlas.name

            # Assert mif end.
            assert mif_lines[4] == '}'

            # Assert new lines at the end of the string.
            assert mif[-2:] == '\n\n'
