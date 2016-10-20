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

        # Case 6: host False (wrong file), docker False, no exception
        varname = "OOMMFWRONGFILE"
        dockername = "dockerwrong"
        raise_exception = False
        status = oc.oommf.status(varname=varname,
                                 dockername=dockername,
                                 raise_exception=raise_exception)
        assert isinstance(status, dict)
        assert status["host"] is False
        assert status["docker"] is False

    def test_call_oommf(self):
        argstr = "+version"
        varname = "OOMMFTCL"
        dockername = "docker"
        raise_exception = True
        dockerimage = "joommf/oommf"
        for where in [None, "host", "docker"]:
            oc.oommf.call(argstr=argstr,
                          varname=varname,
                          dockername=dockername,
                          raise_exception=raise_exception,
                          dockerimage=dockerimage,
                          where=where)

    def test_version(self):
        version = oc.oommf.version(where=None)
        assert isinstance(version, str)
        assert "." in version
        assert version[0].isdigit() and version[-1].isdigit()
        assert 5 < len(version) < 10

        version = oc.oommf.version(where="host")
        assert isinstance(version, str)
        assert "." in version
        assert version[0].isdigit() and version[-1].isdigit()
        assert 5 < len(version) < 10

        version = oc.oommf.version(where="docker")
        assert isinstance(version, str)
        assert "." in version
        assert version[0].isdigit() and version[-1].isdigit()
        assert 5 < len(version) < 10

    def test_where_to_run(self):
        # Case 1: choose "host", both working
        where = None
        varname = "OOMMFTCL"
        dockername = "docker"
        raise_exception = True
        where = oc.oommf.oommf.where_to_run(where=where, varname=varname,
                                            dockername=dockername,
                                            raise_exception=raise_exception)
        assert where == "host"

        # Case 2: choose "host", only host working
        where = None
        varname = "OOMMFTCL"
        dockername = "wrongdocker"
        raise_exception = True
        where = oc.oommf.oommf.where_to_run(where=where, varname=varname,
                                            dockername=dockername,
                                            raise_exception=raise_exception)
        assert where == "host"

        # Case 2: choose "docker", only docker working
        where = None
        varname = "WRONGOMMFPATH"
        dockername = "docker"
        raise_exception = True
        where = oc.oommf.oommf.where_to_run(where=where, varname=varname,
                                            dockername=dockername,
                                            raise_exception=raise_exception)
        assert where == "docker"
