import os
import glob
import shutil
import pytest
import oommfc as oc
from .test_driver import TestDriver


class TestMinDriver(TestDriver):
    def test_script(self):
        md = oc.MinDriver()

        script = md._script(self.system)

        assert script[0] == "#"
        assert script[-1] == "1"
        assert script.count("#") == 5
        assert script.count("Specify") == 3
        assert script.count("Destination") == 2
        assert script.count("Schedule") == 2
        assert script.count("mmArchive") == 2
        assert script.count("Stage") == 2

        assert "Oxs_CGEvolve" in script
        assert "Oxs_MinDriver" in script
        assert "Oxs_FileVectorField" in script

        if os.path.exists('tds'):
            shutil.rmtree('tds')

    @pytest.mark.oommf
    def test_drive(self):
        md = oc.MinDriver()

        md.drive(self.system)

        dirname = os.path.join("tds", "drive-{}".format(self.system.drive_number-1))
        assert os.path.exists(dirname)
        miffilename = os.path.join(dirname, "tds.mif")
        assert os.path.isfile(miffilename)

        omf_files = list(glob.iglob(os.path.join(dirname, '*.omf')))
        odt_files = list(glob.iglob(os.path.join(dirname, '*.odt')))

        assert len(omf_files) == 2
        omffilename = os.path.join(dirname, "m0.omf")
        assert omffilename in omf_files

        assert len(odt_files) == 1

        if os.path.exists('tds'):
            shutil.rmtree('tds')
