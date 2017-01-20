import subprocess
import pytest
import oommfc as oc


def test_exception_is_raised_if_no_OOMMF():
    dockername = "docker-executable-name-like-this-doesnt-exist"
    dockerimage = "joommf/oommf"
    oommf = oc.OOMMF(varname="OOMMFTCL", dockername=dockername,
                     dockerimage=dockerimage, where="docker")

    # expect exception as docker executable doesn't exist:
    with pytest.raises(FileNotFoundError):
        oommf.call(argstr="+version")

    # The next test only makes sense if we have no docker deamon running.
    # So let's check for that
    status, output = subprocess.getstatusoutput('docker ps')
    assert status is not 0, "Seems that you have a docker running."\
        "Stop it (output={})".format(output)

    # expect "Cannot connect to the Docker daemon. Is the docker daemon running on this host?'"
    assert 'Docker' in output
    assert 'running on this host' in output

    # would be good to check for RuntimeError to be raised if docker is
    # not running, but don't know how to force that.
    # expect exception as docker executable doesn't exist:
    dockername = "docker"
    dockerimage = "joommf/oommf"
    oommf = oc.OOMMF(varname="OOMMFTCL", dockername=dockername,
                     dockerimage=dockerimage, where="docker")

    with pytest.raises(RuntimeError):
        oommf.call(argstr="+version")
