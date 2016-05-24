import pytest
from oommfc import BoxAtlas


class TestBoxAtlas(object):
    def setup(self):
        # Set of valid arguments.
        self.args1 = [[(0, 0, 0), (5, 5, 5), 'atlas1', 'rn1'],
                      [(0, 0, 0), (5e-9, 5e-9, 5e-9), 'atlas2', 'rn2'],
                      [(-1.5e-9, -5e-9, 0), (1.5e-9, 15e-9, 16e-9),
                       'atlas3', 'rn3']]

        # Set of invalid arguments.
        self.args2 = [[(5, 0, 0), (0, 5, 5), 'atlas4', 'rn4'],
                      [(0, 5, 0), (5, 0, 5), 'atlas5', 'rn5'],
                      [(0, 0, 5), (5, 5, 0), 'atlas6', 'rn6'],
                      [(0, 0, 0), (5, 5, 5), 1e-9, 'rn7'],
                      [(0, 0, 0), (5, 5, 5), 'atlas', 17]]

    def test_init(self):
        # Valid arguments.
        for arg in self.args1:
            cmin = arg[0]
            cmax = arg[1]
            name = arg[2]
            regionname = arg[3]

            ba = BoxAtlas(cmin, cmax, name, regionname)

            assert ba.cmin == cmin
            assert ba.cmax == cmax
            assert ba.name == name
            assert ba.regionname == regionname

            assert isinstance(ba.cmin, tuple)
            assert isinstance(ba.cmax, tuple)
            assert isinstance(ba.name, str)
            assert isinstance(ba.regionname, str)

    def test_init_exceptions(self):
        # Invalid arguments (ValueError expected).
        for arg in self.args2:
            with pytest.raises(ValueError):
                cmin = arg[0]
                cmax = arg[1]
                name = arg[2]
                regionname = arg[3]

                ba = BoxAtlas(cmin, cmax, name, regionname)

    def test_get_mif(self):
        for arg in self.args1:
            cmin = arg[0]
            cmax = arg[1]
            name = arg[2]
            regionname = arg[3]

            ba = BoxAtlas(cmin, cmax, name, regionname)

            mif = ba.get_mif()
            mif_lines = ba.get_mif().split('\n')

            # Assert comment.
            l1 = mif_lines[0].split()
            assert l1[0] == '#'
            assert l1[1] == 'BoxAtlas'

            # Assert Specify line.
            l = mif_lines[1].split()
            assert l[0] == 'Specify'
            assert l[1].split(':')[0] == 'Oxs_BoxAtlas'
            assert l[1].split(':')[1] == name
            assert l[2] == '{'

            # Assert range lines.
            assert mif_lines[2][0] == '\t'
            l = mif_lines[2].split()
            assert l[0] == 'xrange'
            assert l[1] == '{'
            assert float(l[2]) == cmin[0]
            assert float(l[3]) == cmax[0]
            assert l[4] == '}'

            # Assert range lines.
            assert mif_lines[3][0] == '\t'
            l = mif_lines[3].split()
            assert l[0] == 'yrange'
            assert l[1] == '{'
            assert float(l[2]) == cmin[1]
            assert float(l[3]) == cmax[1]
            assert l[4] == '}'

            # Assert range lines.
            assert mif_lines[4][0] == '\t'
            l = mif_lines[4].split()
            assert l[0] == 'zrange'
            assert l[1] == '{'
            assert float(l[2]) == cmin[2]
            assert float(l[3]) == cmax[2]
            assert l[4] == '}'

            # Assert region name.
            assert mif_lines[5][0] == '\t'
            l = mif_lines[5].split()
            assert l[0] == 'name'
            assert l[1] == regionname

            # Assert mif end.
            assert mif_lines[6] == '}'

            # Assert new lines at the end of the string.
            assert mif[-2:] == '\n\n'
