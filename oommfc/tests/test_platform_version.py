import pytest
import oommfc

@pytest.mark.skip
def test_version_returns():
    runner = oommfc.get_oommf_runner()
    runner.version()

@pytest.mark.skip
def test_platform_returns():
    runner = oommfc.get_oommf_runner()
    runner.version()
