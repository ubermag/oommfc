import oommfc

def test_version_returns():
    runner = oommfc.get_oommf_runner()
    runner.version()
    
def test_platform_returns():
    runner = oommfc.get_oommf_runner()
    runner.version()
