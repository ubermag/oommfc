import pytest
from oommfc.hamiltonian import UniformExchange


class TestUniformExchange(object):
    def setup(self):
        # Set of valid arguments.
        self.args1 = [1, 2, 1e-11, 1e-12, 1e-13, 1e-14, 1e6]

    def test_script(self):
        for A in self.args1:
            exchange = UniformExchange(A)

            mif = exchange.script()
            mif_lines = exchange.script().split('\n')

            # Assert comment.
            l = mif_lines[0].split()
            assert l[0] == '#'
            assert l[1] == 'UniformExchange'

            # Assert Specify line.
            l = mif_lines[1].split()
            assert l[0] == 'Specify'
            assert l[1] == 'Oxs_UniformExchange'
            assert l[2] == '{'

            # Assert step line.
            assert mif_lines[2][0] == '\t'
            l = mif_lines[2].split()
            assert l[0] == 'A'
            assert float(l[1]) == A

            # Assert mif end.
            assert mif_lines[3] == '}'

            # Assert new lines at the end of the string.
            assert mif[-2:] == '\n\n'
