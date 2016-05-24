import pytest
from oommfc.energies import UniformExchange


class TestUniformExchange(object):
    def setup(self):
        # Set of valid arguments.
        self.args1 = [1, 2, 1e-11, 1e-12, 1e-13, 1e-14, 1e6]

        # Set of invalid arguments.
        self.args2 = [-1, -2.1, 'a', (1, 2), 0, '0', [1, 2, 3]]

    def test_init(self):
        # Valid arguments.
        for A in self.args1:
            exchange = UniformExchange(A)

            assert exchange.A == A
            assert isinstance(exchange.A, (int, float))

    def test_init_exceptions(self):
        # Invalid arguments (ValueError expected).
        for A in self.args2:
            with pytest.raises(ValueError):
                exchange = UniformExchange(A)

    def test_get_mif(self):
        for A in self.args1:
            exchange = UniformExchange(A)

            mif = exchange.get_mif()
            mif_lines = exchange.get_mif().split('\n')

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
