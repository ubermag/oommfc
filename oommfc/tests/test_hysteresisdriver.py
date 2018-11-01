import os
import glob
import shutil
import pytest
import oommfc as oc
from .test_driver import TestDriver


class TestHysteresisDriver(TestDriver):
    def test_script(self):
        hd = oc.HysteresisDriver()

        script = hd._script(self.system, Hmin=(0, 0, 0),
                            Hmax=(10, 10, 10), n=10)

        assert script[0] == '#'
        assert script[-1] == '1'
        assert script.count('#') == 6
        assert script.count('Specify') == 4
        assert script.count('Destination') == 2
        assert script.count('Schedule') == 2
        assert script.count('mmArchive') == 2
        assert script.count('Stage') == 2

        assert 'Oxs_UZeeman' in script
        assert 'Oxs_CGEvolve' in script
        assert 'Oxs_MinDriver' in script
        assert 'Oxs_FileVectorField' in script

        if os.path.exists('tds'):
            shutil.rmtree('tds')

    @pytest.mark.oommf
    def test_drive(self):
        hd = oc.HysteresisDriver()

        hd.drive(self.system, Hmin=(0, 0, 0), Hmax=(1, 1, 1), n=10)

        dirname = os.path.join('tds', 'drive-{}'.format(self.system.drive_number-1))
        assert os.path.exists(dirname)
        miffilename = os.path.join(dirname, 'tds.mif')
        assert os.path.isfile(miffilename)

        omf_files = list(glob.iglob(os.path.join(dirname, '*.omf')))
        odt_files = list(glob.iglob(os.path.join(dirname, '*.odt')))

        assert len(omf_files) == 22
        omffilename = os.path.join(dirname, 'm0.omf')
        assert omffilename in omf_files

        assert len(odt_files) == 1

        if os.path.exists('tds'):
            shutil.rmtree('tds')
