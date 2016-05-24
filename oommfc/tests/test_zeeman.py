import pytest
from oommfc.energies import FixedZeeman


class TestFixedZeeman(object):
    def setup(self):
        # Set of valid arguments.
        self.args1 = [[(1, 1.4, 1), 1, 'fixedzeeman1'],
                      [(0, 0, 1), 1e6, 'fixedzeeman2'],
                      [[1.2, 0, 0], 1e-6, 'fixedzeeman3'],
                      [(0.56, 1.98, -1.1), 15, 'fixedzeeman4'],
                      [[15, 0, 3.14], 1e7, 'fixedzeeman5']]

        # Set of invalid arguments.
        self.args2 = [[(1, 1), 1, 'fixedzeeman1'],
                      [1, 1e6, 'fixedzeeman2'],
                      [(1.2, 0, 0, 5), 1e-6, 'fixedzeeman3'],
                      [(0.56, 1.98, -1.1), (1, 1), 'fixedzeeman4'],
                      [(15, 0, 3.14), 1e7, 5]]

    def test_init(self):
        # Valid arguments.
        for args in self.args1:
            H = args[0]
            multiplier = args[1]
            name = args[2]

            fz = FixedZeeman(H, multiplier, name)

            assert fz.H == H
            assert isinstance(fz.H, (tuple, list))
            assert fz.multiplier == multiplier
            assert isinstance(fz.multiplier, (int, float))
            assert fz.name == name
            assert isinstance(fz.name, str)

    def test_init_exceptions(self):
        # Invalid arguments (ValueError expected).
        for args in self.args2:
            with pytest.raises(ValueError):
                H = args[0]
                multiplier = args[1]
                name = args[2]

                fz = FixedZeeman(H, multiplier, name)

    def test_get_mif(self):
        for args in self.args1:
            H = args[0]
            multiplier = args[1]
            name = args[2]

            fz = FixedZeeman(H, multiplier, name)

            mif = fz.get_mif()
            mif_lines = fz.get_mif().split('\n')

            # Assert comment.
            l = mif_lines[0].split()
            assert l[0] == '#'
            assert l[1] == 'FixedZeeman'

            # Assert Specify line.
            l = mif_lines[1].split()
            assert l[0] == 'Specify'
            assert l[1].split(':')[0] == 'Oxs_FixedZeeman'
            assert l[1].split(':')[1] == name
            assert l[2] == '{'

            assert mif_lines[2][0] == '\t'
            l = mif_lines[2].split()
            assert l[0] == 'field'
            assert l[1] == '{'

            assert mif_lines[3][0:2] == '\t\t'
            l = mif_lines[3].split()
            assert l[0] == 'Oxs_UniformVectorField'
            assert l[1] == '{'

            assert mif_lines[4][0:3] == '\t\t\t'
            l = mif_lines[4].split()
            assert l[0] == 'vector'
            assert l[1] == '{'
            assert l[2] == str(H[0])
            assert l[3] == str(H[1])
            assert l[4] == str(H[2])
            assert l[5] == '}'

            assert mif_lines[5][0:2] == '\t\t'
            l = mif_lines[5].split()
            assert l[0] == '}'

            assert mif_lines[6][0] == '\t'
            l = mif_lines[6].split()
            assert l[0] == '}'

            assert mif_lines[7][0] == '\t'
            l = mif_lines[7].split()
            assert l[0] == 'multiplier'
            assert l[1] == str(multiplier)

            # Assert mif end.
            assert mif_lines[8] == '}'

            # Assert new lines at the end of the string.
            assert mif[-2:] == '\n\n'
