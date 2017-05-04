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

        assert script[0] == "#"
        assert script[-1] == "1"
        assert script.count("#") == 6
        assert script.count("Specify") == 4
        assert script.count("Destination") == 2
        assert script.count("Schedule") == 2
        assert script.count("mmArchive") == 2
        assert script.count("Stage") == 2

        assert "Oxs_UZeeman" in script
        assert "Oxs_CGEvolve" in script
        assert "Oxs_MinDriver" in script
        assert "Oxs_FileVectorField" in script

    def test_save_mif(self):
        hd = oc.HysteresisDriver()

        hd._makedir(self.system)
        hd._save_mif(self.system, Hmin=(0, 0, 0), Hmax=(1, 1, 1), n=10)

        miffilename = os.path.join("tds", "tds.mif")
        assert os.path.isfile(miffilename)

        lines = open(miffilename, "r").readlines()
        assert lines[0] == "# MIF 2.1\n"
        assert lines[-1][-1] == "1"

        shutil.rmtree("tds")

    @pytest.mark.oommf
    def test_drive(self):
        hd = oc.HysteresisDriver()

        hd.drive(self.system, Hmin=(0, 0, 0), Hmax=(1, 1, 1), n=10)

        dirname = os.path.join("tds", "")
        assert os.path.exists(dirname)
        miffilename = os.path.join("tds", "tds.mif")
        assert os.path.isfile(miffilename)

        omf_files = list(glob.iglob("tds/*.omf"))
        odt_files = list(glob.iglob("tds/*.odt"))

        assert len(omf_files) == 22
        omffilename = os.path.join("tds", "m0.omf")
        assert omffilename in omf_files

        assert len(odt_files) == 1

        shutil.rmtree("tds")
