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

    def test_save_mif(self):
        md = oc.MinDriver()

        md._makedir(self.system)
        md._save_mif(self.system)

        miffilename = os.path.join("tds", "tds.mif")
        assert os.path.isfile(miffilename)

        lines = open(miffilename, "r").readlines()
        assert lines[0] == "# MIF 2.1\n"
        assert lines[-1][-1] == "1"

        shutil.rmtree("tds")

    @pytest.mark.oommf
    def test_drive(self):
        md = oc.MinDriver()

        md.drive(self.system)

        dirname = os.path.join("tds", "")
        assert os.path.exists(dirname)
        miffilename = os.path.join("tds", "tds.mif")
        assert os.path.isfile(miffilename)

        omf_files = list(glob.iglob("tds/*.omf"))
        odt_files = list(glob.iglob("tds/*.odt"))

        assert len(omf_files) == 2
        omffilename = os.path.join("tds", "m0.omf")
        assert omffilename in omf_files

        assert len(odt_files) == 1

        shutil.rmtree("tds")
