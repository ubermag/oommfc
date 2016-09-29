import os
import glob
import oommfc as oc
from .test_driver import TestDriver


class TestMinDriver(TestDriver):
    def test_script(self):
        md = oc.MinDriver()

        script = md.script(self.system)

        assert script[0] == "#"
        assert script[-1] == "1"
        assert script.count("#") == 3
        assert script.count("Specify") == 2
        assert script.count("Destination") == 2
        assert script.count("Schedule") == 2
        assert script.count("mmArchive") == 2
        assert script.count("Stage") == 2

        assert "Oxs_CGEvolve" in script
        assert "Oxs_MinDriver" in script
        assert "Oxs_FileVectorField" in script

        lines = script.split("\n")
        assert lines[8] == "  Ms {}".format(8e5)
        assert lines[13] == "      file m0.omf"
        assert lines[16] == "  basename tds"

    def test_save_mif(self):
        md = oc.MinDriver()

        md._makedir(self.system)
        md._save_mif(self.system)

        assert os.path.isfile("tds/tds.mif")

        lines = open("tds/tds.mif", "r").readlines()
        assert lines[0] == "# MIF 2.1\n"
        assert lines[-1][-1] == "1"

        os.system("rm -r tds/")

    def test_drive(self):
        md = oc.MinDriver()

        md.drive(self.system)

        assert os.path.exists("tds/")
        assert os.path.isfile("tds/tds.mif")

        omf_files = list(glob.iglob("tds/*.omf"))
        odt_files = list(glob.iglob("tds/*.odt"))

        assert len(omf_files) == 2
        assert "tds/m0.omf" in omf_files

        assert len(odt_files) == 1

        os.system("rm -r tds/")
