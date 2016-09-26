import pytest
from oommfc import TimeDriver, MinDriver


class TestTimeDriver(object):
    def setup(self):
        # Set of valid arguments.
        self.args1 = [['e1', 1, 1, 'm1', 1e6, (0, 0, 1), 'n1'],
                      ['e2', 1e-9, 5, 'm2', 5e6, (1, 0, 0), 'n2'],
                      ['e3', 1e-12, 10, 'm3', 1e-6, 'file.ovf', 'n3'],
                      ['e4', 0.1, 20, 'm4', 1, 'string.ext', 'n4']]

        # Set of invalid arguments.
        self.args2 = [[1, 1, 1, 'm1', 1e6, (0, 0, 1), 'n1'],
                      ['e2', 'a', 5, 'm2', 5e6, (1, 0, 0), 'n2'],
                      ['e3', 1e-12, [1, 2], 'm3', 1e-6, 'file.ovf', 'ne3'],
                      ['e4', 0.1, 20, 'm4', 1, 'string.ext', 31],
                      ['e5', 1, 1, (1, 2), 1e6, (0, 0, 1), 'n1'],
                      ['e1', 1, 1, 'm1', -1e6, (0, 0, 1), 'n1'],
                      ['e1', 1, 1, 'm1', 1e6, 256, 'n1']]

    def test_init(self):
        # Valid arguments.
        for arg in self.args1:
            evolver = arg[0]
            stopping_time = arg[1]
            stage_count = arg[2]
            mesh = arg[3]
            Ms = arg[4]
            m0 = arg[5]
            basename = arg[6]

            driver = TimeDriver(evolver, stopping_time, stage_count,
                                mesh, Ms, m0, basename)

            assert driver.evolver == evolver
            assert driver.stopping_time == stopping_time
            assert driver.stage_count == stage_count
            assert driver.mesh == mesh
            assert driver.Ms == Ms
            assert driver.m0 == m0
            assert driver.basename == basename

    def test_init_exceptions(self):
        # Invalid arguments (ValueError expected).
        for arg in self.args2:
            evolver = arg[0]
            stopping_time = arg[1]
            stage_count = arg[2]
            mesh = arg[3]
            Ms = arg[4]
            m0 = arg[5]
            basename = arg[6]
            with pytest.raises(ValueError):
                driver = TimeDriver(evolver, stopping_time, stage_count,
                                    mesh, Ms, m0, basename)

    def test_get_mif(self):
        for arg in self.args1:
            evolver = arg[0]
            stopping_time = arg[1]
            stage_count = arg[2]
            mesh = arg[3]
            Ms = arg[4]
            m0 = arg[5]
            basename = arg[6]

            driver = TimeDriver(evolver, stopping_time, stage_count,
                                mesh, Ms, m0, basename)

            mif = driver.get_mif()
            mif_lines = driver.get_mif().split('\n')

            # Assert comment.
            l = mif_lines[0].split()
            assert l[0] == '#'
            assert l[1] == 'TimeDriver'

            # Assert Specify line.
            l = mif_lines[1].split()
            assert l[0] == 'Specify'
            assert l[1].split(':')[0] == 'Oxs_TimeDriver'
            assert l[2] == '{'

            # Assert parameters lines
            assert mif_lines[2][0] == '\t'
            l = mif_lines[2].split()
            assert l[0] == 'evolver'
            assert l[1] == evolver

            # Assert parameters lines
            assert mif_lines[3][0] == '\t'
            l = mif_lines[3].split()
            assert l[0] == 'stopping_time'
            assert float(l[1]) == stopping_time

            # Assert parameters lines
            assert mif_lines[4][0] == '\t'
            l = mif_lines[4].split()
            assert l[0] == 'stage_count'
            assert int(l[1]) == stage_count

            # Assert parameters lines
            assert mif_lines[5][0] == '\t'
            l = mif_lines[5].split()
            assert l[0] == 'mesh'
            assert l[1] == ':' + mesh

            # Assert parameters lines
            assert mif_lines[6][0] == '\t'
            l = mif_lines[6].split()
            assert l[0] == 'Ms'
            assert float(l[1]) == Ms

            # Assert parameters lines
            assert mif_lines[7][0] == '\t'
            l = mif_lines[7].split()
            assert l[0] == 'm0'
            assert l[1] == '{'

            # Assert initial state definition.
            if isinstance(m0, (list, tuple)):
                assert mif_lines[8][0:2] == '\t\t'
                l = mif_lines[8].split()
                assert l[0] == 'Oxs_UniformVectorField'
                assert l[1] == '{'

                assert mif_lines[9][0:3] == '\t\t\t'
                l = mif_lines[9].split()
                assert l[0] == 'vector'
                assert l[1] == '{'
                assert float(l[2]) == m0[0]
                assert float(l[3]) == m0[1]
                assert float(l[4]) == m0[2]
                assert l[5] == '}'

                assert mif_lines[10][0:2] == '\t\t'
                l = mif_lines[10].split()
                assert l[0] == '}'

                n = 10

            elif isinstance(m0, str):
                assert mif_lines[8][0:2] == '\t\t'
                l = mif_lines[8].split()
                assert l[0] == 'Oxs_FileVectorField'
                assert l[1] == '{'

                assert mif_lines[9][0:3] == '\t\t\t'
                l = mif_lines[9].split()
                assert l[0] == 'atlas'
                assert l[1] == ':atlas'

                assert mif_lines[10][0:3] == '\t\t\t'
                l = mif_lines[10].split()
                assert l[0] == 'norm'
                assert float(l[1]) == 1

                assert mif_lines[11][0:3] == '\t\t\t'
                l = mif_lines[11].split()
                assert l[0] == 'file'
                assert l[1] == m0

                assert mif_lines[12][0:2] == '\t\t'
                l = mif_lines[12].split()
                assert l[0] == '}'

                n = 12

            assert mif_lines[n+1] == '\t}'

            assert mif_lines[n+2][0] == '\t'
            l = mif_lines[n+2].split()
            assert l[0] == 'basename'
            assert l[1] == basename

            l = mif_lines[n+3]
            assert l == '\tvector_field_output_format {text %\#.8g}'

            # Assert mif end.
            assert mif_lines[n+4] == '}'

            # Assert new lines at the end of the string.
            assert mif[-2:] == '\n\n'


class TestMinDriver(object):
    def setup(self):
        # Set of valid arguments.
        self.args1 = [['e1', 1, 'm1', 1e6, (0, 0, 1), 'n1'],
                      ['e2', 1e-9, 'm2', 5e6, (1, 0, 0), 'n2'],
                      ['e3', 1e-12, 'm3', 1e-6, 'file.ovf', 'n3'],
                      ['e4', 0.1, 'm4', 1, 'string.ext', 'n4']]

        # Set of valid arguments.
        self.args2 = [[1, 1, 'm1', 1e6, (0, 0, 1), 'n1'],
                      ['e2', 'a', 'm2', 5e6, (1, 0, 0), 'n2'],
                      ['e3', 1e-12, 'm3', -1e-6, 'file.ovf', 'ne3'],
                      ['e4', 0.1, 'm4', 1, 'string.ext', 31],
                      ['e5', 1, 31, 1e6, (0, 0, 1), 'n1'],
                      ['e6', 1, 'm1', 1e6, 1e-6, 'n1']]

    def test_init(self):
        # Valid arguments.
        for arg in self.args1:
            evolver = arg[0]
            stopping_mxHxm = arg[1]
            mesh = arg[2]
            Ms = arg[3]
            m0 = arg[4]
            basename = arg[5]

            driver = MinDriver(evolver, stopping_mxHxm, mesh, Ms, m0, basename)

            assert driver.evolver == evolver
            assert driver.stopping_mxHxm == stopping_mxHxm
            assert driver.mesh == mesh
            assert driver.Ms == Ms
            assert driver.m0 == m0
            assert driver.basename == basename

    def test_init_exceptions(self):
        # Invalid arguments (ValueError expected).
        for arg in self.args2:
            evolver = arg[0]
            stopping_mxHxm = arg[1]
            mesh = arg[2]
            Ms = arg[3]
            m0 = arg[4]
            basename = arg[5]
            with pytest.raises(ValueError):
                driver = MinDriver(evolver, stopping_mxHxm,
                                   mesh, Ms, m0, basename)

    def test_get_mif(self):
        for arg in self.args1:
            evolver = arg[0]
            stopping_mxHxm = arg[1]
            mesh = arg[2]
            Ms = arg[3]
            m0 = arg[4]
            basename = arg[5]

            driver = MinDriver(evolver, stopping_mxHxm, mesh, Ms, m0, basename)

            mif = driver.get_mif()
            mif_lines = driver.get_mif().split('\n')

            # Assert comment.
            l = mif_lines[0].split()
            assert l[0] == '#'
            assert l[1] == 'MinDriver'

            # Assert Specify line.
            l = mif_lines[1].split()
            assert l[0] == 'Specify'
            assert l[1].split(':')[0] == 'Oxs_MinDriver'
            assert l[2] == '{'

            # Assert parameters lines
            assert mif_lines[2][0] == '\t'
            l = mif_lines[2].split()
            assert l[0] == 'evolver'
            assert l[1] == evolver

            # Assert parameters lines
            assert mif_lines[3][0] == '\t'
            l = mif_lines[3].split()
            assert l[0] == 'stopping_mxHxm'
            assert float(l[1]) == stopping_mxHxm

            # Assert parameters lines
            assert mif_lines[4][0] == '\t'
            l = mif_lines[4].split()
            assert l[0] == 'mesh'
            assert l[1] == ':' + mesh

            # Assert parameters lines
            assert mif_lines[5][0] == '\t'
            l = mif_lines[5].split()
            assert l[0] == 'Ms'
            assert float(l[1]) == Ms

            # Assert parameters lines
            assert mif_lines[6][0] == '\t'
            l = mif_lines[6].split()
            assert l[0] == 'm0'
            assert l[1] == '{'

            # Assert initial state definition.
            if isinstance(m0, (list, tuple)):
                assert mif_lines[7][0:2] == '\t\t'
                l = mif_lines[7].split()
                assert l[0] == 'Oxs_UniformVectorField'
                assert l[1] == '{'

                assert mif_lines[8][0:3] == '\t\t\t'
                l = mif_lines[8].split()
                assert l[0] == 'vector'
                assert l[1] == '{'
                assert float(l[2]) == m0[0]
                assert float(l[3]) == m0[1]
                assert float(l[4]) == m0[2]
                assert l[5] == '}'

                assert mif_lines[9][0:2] == '\t\t'
                l = mif_lines[9].split()
                assert l[0] == '}'

                n = 9

            elif isinstance(m0, str):
                assert mif_lines[7][0:2] == '\t\t'
                l = mif_lines[7].split()
                assert l[0] == 'Oxs_FileVectorField'
                assert l[1] == '{'

                assert mif_lines[8][0:3] == '\t\t\t'
                l = mif_lines[8].split()
                assert l[0] == 'atlas'
                assert l[1] == ':atlas'

                assert mif_lines[9][0:3] == '\t\t\t'
                l = mif_lines[9].split()
                assert l[0] == 'norm'
                assert float(l[1]) == 1

                assert mif_lines[10][0:3] == '\t\t\t'
                l = mif_lines[10].split()
                assert l[0] == 'file'
                assert l[1] == m0

                assert mif_lines[11][0:2] == '\t\t'
                l = mif_lines[11].split()
                assert l[0] == '}'

                n = 11

            assert mif_lines[n+1] == '\t}'

            assert mif_lines[n+2][0] == '\t'
            l = mif_lines[n+2].split()
            assert l[0] == 'basename'
            assert l[1] == basename

            l = mif_lines[n+3]
            assert l == '\tvector_field_output_format {text %\#.8g}'

            # Assert mif end.
            assert mif_lines[n+4] == '}'

            # Assert new lines at the end of the string.
            assert mif[-2:] == '\n\n'
