import pytest
import oommfc as oc


class TestOOMMF:
    def test_getenv(self):
        oommf = oc.OOMMF()
        with pytest.raises(EnvironmentError):
            oommf.getenv("NONEXISTINGENV123")
