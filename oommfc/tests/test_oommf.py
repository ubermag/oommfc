import pytest
import oommfc as oc


class TestOOMMF:
    def test_status(self):
        # Case 1: host True, docker True
        varname = "OOMMFTCL"
        dockername = "docker"
        raise_exception = True
        status = oc.oommf.status(varname=varname,
                                 dockername=dockername,
                                 raise_exception=raise_exception)
        assert isinstance(status, dict)
        assert status["host"] is True
        assert status["docker"] is True

        # Case 2: host True, docker False
        varname = "OOMMFTCL"
        dockername = "dockerwrongname"
        raise_exception = True
        status = oc.oommf.status(varname=varname,
                                 dockername=dockername,
                                 raise_exception=raise_exception)
        assert isinstance(status, dict)
        assert status["host"] is True
        assert status["docker"] is False

        # Case 3: host False (wrong varname), docker True
        varname = "OOMMFWRONGVARNAME"
        dockername = "docker"
        raise_exception = True
        status = oc.oommf.status(varname=varname,
                                 dockername=dockername,
                                 raise_exception=raise_exception)
        assert isinstance(status, dict)
        assert status["host"] is False
        assert status["docker"] is True

        # Case 4: host False (wrong path), docker True
        varname = "OOMMFWRONGPATH"
        dockername = "docker"
        raise_exception = True
        status = oc.oommf.status(varname=varname,
                                 dockername=dockername,
                                 raise_exception=raise_exception)
        assert isinstance(status, dict)
        assert status["host"] is False
        assert status["docker"] is True

        # Case 4: host False (wrong path), docker False, no exception
        varname = "WRONGWRONGWRONG"
        dockername = "dockerwrong"
        raise_exception = False
        status = oc.oommf.status(varname=varname,
                                 dockername=dockername,
                                 raise_exception=raise_exception)
        assert isinstance(status, dict)
        assert status["host"] is False
        assert status["docker"] is False


        # Case 5: host False (wrong path), docker False, raise exception
        varname = "WRONGWRONGWRONG"
        dockername = "dockerwrong"
        raise_exception = True
        with pytest.raises(EnvironmentError):
            status = oc.oommf.status(varname=varname,
                                     dockername=dockername,
                                     raise_exception=raise_exception)


    def test_call_oommf(self):
        oc.oommf.call(argstr="+v", where=None)
        oc.oommf.call(argstr="+v", where="host")
        oc.oommf.call(argstr="+v", where="docker")
