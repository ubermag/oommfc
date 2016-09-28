import os
import oommfc as oc
from .test_driver import TestDriver


class TestMinDriver(TestDriver):
    def test_script(self):
        driver = oc.MinDriver()

        script = driver.script(self.system)

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
        driver = oc.MinDriver()

        driver._makedir(self.system)
        driver._save_mif(self.system)

        assert os.path.isfile("tds/tds.mif")

        lines = open("tds/tds.mif", "r").readlines()
        assert lines[0] == "# MIF 2.1\n"
        assert lines[-1][-1] == "1"

        os.system("rm -r tds/")
