import sys
import pytest
import oommfc as oc
import micromagneticmodel.tests as mmt


def check_script(script, contains):
    assert script.count('\n') == 9
    assert script[0] == '#'
    assert script[-1] == '\n'

    for content in contains:
        assert content in script
            
class TestDMI(mmt.TestDMI):
    @pytest.mark.skipif(sys.platform == 'win32',
                        reason='Crystalographic class not supported on Windows.')
    def test_script_to(self):
        for D in self.valid_args:
            dmi = oc.DMI(D, crystalclass='t')
            check_script(dmi._script, contains=['Oxs_DMI_T'])

            dmi = oc.DMI(D, crystalclass='o')
            check_script(dmi._script, contains=['Oxs_DMI_T'])

    @pytest.mark.skipif(sys.platform == 'win32',
                        reason='Crystalographic class not supported on Windows.')
    def test_script_d2d(self):
        for D in self.valid_args:
            dmi = oc.DMI(D, crystalclass='d2d')
            check_script(dmi._script, contains=['Oxs_DMI_D2d'])

    @pytest.mark.skipif(sys.platform == 'win32',
                        reason='Crystalographic class not supported on Windows.')
    def test_script_cnv_linux_mac(self):
        for D in self.valid_args:
            dmi = oc.DMI(D, crystalclass='cnv')
            check_script(dmi._script, contains=['Oxs_DMI_Cnv'])

    @pytest.mark.skipif(sys.platform != 'win32',
                        reason='Crystalographic class not supported on Windows.')
    def test_script_cnv_win(self):
        for D in self.valid_args:
            dmi = oc.DMI(D, crystalclass='cnv')
            check_script(dmi._script, contains=['Oxs_DMExchange6Ngbr'])

    @pytest.mark.skipif(sys.platform != 'win32',
                        reason='Crystalographic class not supported on Windows.')
    def test_valueerror(self):
        with pytest.raises(ValueError):
            dmi = oc.DMI(D=1, crystalclass='t')
            dmi._script
