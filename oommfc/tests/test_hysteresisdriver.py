import os
import glob
import oommfc as oc
from .test_driver import TestDriver


class TestHysteresisDriver(TestDriver):
    def test_script(self):
        hd = oc.HysteresisDriver()

        script = hd.script(self.system, Hmin=(0, 0, 0),
                           Hmax=(10, 10, 10), n=10)

        assert script[0] == "#"
        assert script[-1] == "1"
        assert script.count("#") == 4
        assert script.count("Specify") == 3
        assert script.count("Destination") == 2
        assert script.count("Schedule") == 2
        assert script.count("mmArchive") == 2
        assert script.count("Stage") == 2

        assert "Oxs_UZeeman" in script
        assert "Oxs_CGEvolve" in script
        assert "Oxs_MinDriver" in script
        assert "Oxs_FileVectorField" in script
