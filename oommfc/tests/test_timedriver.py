import os
import glob
import oommfc as oc
from .test_driver import TestDriver


class TestTimeDriver(TestDriver):
    def test_script(self):
        driver = oc.TimeDriver()
        t = 1e-9
        n = 120
        script = driver.script(self.system, t=t, n=n)

        assert script[0] == "#"
        assert script[-1] == "1"
        assert script.count("#") == 3
        assert script.count("Specify") == 2
        assert script.count("Destination") == 2
        assert script.count("Schedule") == 2
        assert script.count("mmArchive") == 2
        assert script.count("Stage") == 2

        assert "Oxs_RungeKuttaEvolve" in script
        assert "Oxs_TimeDriver" in script
        assert "Oxs_FileVectorField" in script

        lines = script.split("\n")
        alpha = self.system.dynamics.damping.alpha
        assert lines[2] == "  alpha {}".format(alpha)
        gamma = self.system.dynamics.precession.gamma
        assert lines[3] == "  gamma_G {}".format(gamma)
        assert lines[9] == "  stopping_time {}".format(t/n)
        assert lines[11] == "  stage_count {}".format(n)
        assert lines[12] == "  Ms {}".format(8e5)
        assert lines[17] == "      file m0.omf"
        assert lines[20] == "  basename tds"

    def test_save_mif(self):
        driver = oc.TimeDriver()
        t = 1e-9
        n = 120
        driver._makedir(self.system)
        driver._save_mif(self.system, t=t, n=n)

        assert os.path.isfile("tds/tds.mif")

        lines = open("tds/tds.mif", "r").readlines()
        assert lines[0] == "# MIF 2.1\n"
        assert lines[-1][-1] == "1"

        os.system("rm -r tds/")

    def test_drive(self):
        md = oc.TimeDriver()

        md.drive(self.system, t=0.1e-9, n=10)

        assert os.path.exists("tds/")
        assert os.path.isfile("tds/tds.mif")

        omf_files = list(glob.iglob("tds/*.omf"))
        odt_files = list(glob.iglob("tds/*.odt"))

        assert len(omf_files) == 11
        assert "tds/m0.omf" in omf_files

        assert len(odt_files) == 1

        os.system("rm -r tds/")
