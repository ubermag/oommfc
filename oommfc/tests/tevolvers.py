import pytest
from oommfc import RungeKuttaEvolve, CGEvolve


class TestRungeKuttaEvolve(object):
    def setup(self):
        # Set of valid arguments.
        self.args1 = [[1, 1, 1, 'rkf54'],
                      [0.5, 1e5, 0.01, 'rk2'],
                      [0.05, 2.21e5, 5e6, 'rk4'],
                      [0.1, .1, 1e-2, 'rkf54m']]

        # Set of invalid arguments.
        self.args2 = [[-0.1, 1, 1, 'bac'],
                      [0.5, -1e5, 0.01, 'bac'],
                      [0.05, 2.21e5, 'abc', 'rkf54'],
                      [0.1, .1, -1e-2, 'rk2'],
                      [0.1, 0.1, 0.1, 0.1]]

    def test_init(self):
        # Valid arguments.
        for arg in self.args1:
            alpha = arg[0]
            gamma_G = arg[1]
            start_dm = arg[2]
            method = arg[3]

            evolver = RungeKuttaEvolve(alpha, gamma_G, start_dm, method)

            assert evolver.alpha == alpha
            assert isinstance(alpha, (int, float))
            assert evolver.gamma_G == gamma_G
            assert isinstance(gamma_G, (int, float))
            assert evolver.start_dm == start_dm
            assert isinstance(start_dm, (int, float))
            assert evolver.method == method
            assert isinstance(method, str)

    def test_init_exceptions(self):
        # Invalid arguments (ValueError expected).
        for arg in self.args2:
            alpha = arg[0]
            gamma_G = arg[1]
            start_dm = arg[2]
            method = arg[3]

            with pytest.raises(ValueError):
                evolver = RungeKuttaEvolve(alpha, gamma_G, start_dm, method)

    def test_get_mif(self):
        for arg in self.args1:
            alpha = arg[0]
            gamma_G = arg[1]
            start_dm = arg[2]
            method = arg[3]

            evolver = RungeKuttaEvolve(alpha, gamma_G, start_dm, method)

            mif = evolver.get_mif()
            mif_lines = evolver.get_mif().split('\n')

            # Assert comment.
            l = mif_lines[0].split()
            assert l[0] == '#'
            assert l[1] == 'RungeKutta'
            assert l[2] == 'evolver'

            # Assert Specify line.
            l = mif_lines[1].split()
            assert l[0] == 'Specify'
            assert l[1].split(':')[0] == 'Oxs_RungeKuttaEvolve'
            assert l[2] == '{'

            # Assert parameters lines
            assert mif_lines[2][0] == '\t'
            l = mif_lines[2].split()
            assert l[0] == 'alpha'
            assert float(l[1]) == alpha

            # Assert parameters lines
            assert mif_lines[3][0] == '\t'
            l = mif_lines[3].split()
            assert l[0] == 'gamma_G'
            assert float(l[1]) == gamma_G

            # Assert parameters lines
            assert mif_lines[4][0] == '\t'
            l = mif_lines[4].split()
            assert l[0] == 'start_dm'
            assert float(l[1]) == start_dm

            # Assert parameters lines
            assert mif_lines[5][0] == '\t'
            l = mif_lines[5].split()
            assert l[0] == 'method'
            assert l[1] == method

            # Assert mif end.
            assert mif_lines[6] == '}'

            # Assert new lines at the end of the string.
            assert mif[-2:] == '\n\n'


class TestCGEvolve(object):
    def test_get_mif(self):
        evolver = CGEvolve()

        mif = evolver.get_mif()
        mif_lines = evolver.get_mif().split('\n')

        # Assert comment.
        l = mif_lines[0].split()
        assert l[0] == '#'
        assert l[1] == 'CG'
        assert l[2] == 'evolver'

        # Assert Specify line.
        l = mif_lines[1].split()
        assert l[0] == 'Specify'
        assert l[1].split(':')[0] == 'Oxs_CGEvolve'
        assert l[1].split(':')[1] == 'evolver'
        assert l[2] == '{}'

        # Assert new lines at the end of the string.
        assert mif[-2:] == '\n\n'
