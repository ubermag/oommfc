import pytest
from oommfc.energies import UniaxialAnisotropy


class TestUniaxialAnisotropy(object):
    def setup(self):
        # Set of valid arguments.
        self.args1 = [(1, (0, 1, 0)),
                      (5e6, (1, 1, 1)),
                      (-25.6e-3, (0, 0, 1))]

        # Set of invalid arguments.
        self.args2 = [('1', (0, 1, 0)),
                      (5e6, '(1, 1, 1)')]

    def test_init(self):
        # Valid arguments.
        for arg in self.args1:
            K1 = arg[0]
            axis = arg[1]
            anisotropy = UniaxialAnisotropy(K1, axis)

            assert anisotropy.K1 == K1
            assert isinstance(anisotropy.K1, (int, float))
            assert anisotropy.axis == axis
            assert isinstance(anisotropy.axis, (tuple, list))

    def test_init_exceptions(self):
        # Invalid arguments (ValueError expected).
        for arg in self.args2:
            K1 = arg[0]
            axis = arg[1]
            with pytest.raises(ValueError):
                anisotropy = UniaxialAnisotropy(K1, axis)

    def test_get_mif(self):
        for arg in self.args1:
            K1 = arg[0]
            axis = arg[1]

            anisotropy = UniaxialAnisotropy(K1, axis)

            mif = anisotropy.get_mif()
            mif_lines = anisotropy.get_mif().split('\n')

            # Assert comment.
            l = mif_lines[0].split()
            assert l[0] == '#'
            assert l[1] == 'UniaxialAnisotropy'

            # Assert Specify line.
            l = mif_lines[1].split()
            assert l[0] == 'Specify'
            assert l[1] == 'Oxs_UniaxialAnisotropy'
            assert l[2] == '{'

            # Assert step line.
            assert mif_lines[2][0] == '\t'
            l = mif_lines[2].split()
            assert l[0] == 'K1'
            assert float(l[1]) == K1

            # Assert step line.
            assert mif_lines[3][0] == '\t'
            l = mif_lines[3].split()
            assert l[0] == 'axis'
            assert l[1] == '{'
            assert float(l[2]) == axis[0]
            assert float(l[3]) == axis[1]
            assert float(l[4]) == axis[2]
            assert l[5] == '}'

            # Assert mif end.
            assert mif_lines[4] == '}'

            # Assert new lines at the end of the string.
            assert mif[-2:] == '\n\n'
