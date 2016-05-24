import pytest
from oommfc.energies import Demag


class TestDemag(object):
    def test_get_mif(self):
        demag = Demag()

        mif = demag.get_mif()
        mif_lines = mif.split('\n')

        # Assert comment line.
        l = mif_lines[0].split()
        assert l[0] == '#'
        assert l[1] == 'Demag'

        # Assert Specify line.
        assert mif[-2:] == '\n\n'
        l = mif_lines[1].split()
        assert l[0] == 'Specify'
        assert l[1] == 'Oxs_Demag'
        assert l[2] == '{}'
