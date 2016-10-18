import pytest
import oommfc as oc


class TestOOMMF:
    def test_getenv(self):
        oommf = oc.OOMMF()
        with pytest.raises(EnvironmentError):
            oommf.getenv("NONEXISTINGENV123")

    def test_docker_available(self):
        oommf = oc.OOMMF()
        assert isinstance(oommf.docker_available(), bool)
