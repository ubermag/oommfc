import sys
import pytest
import shutil
import testpath
import subprocess
from oommfc.oommf import DockerOOMMFRunner, get_oommf_runner

nonexistant_docker = "docker-executable-name-like-this-does-not-exist"

@pytest.mark.travis
def test_exception_is_raised_if_no_docker():
    runner = DockerOOMMFRunner(docker_exe=nonexistant_docker)

    # expect exception as docker executable doesn't exist:
    with pytest.raises(FileNotFoundError):
        runner.call(argstr="+version")

@pytest.mark.travis
def test_docker_installed_not_running():
    if not shutil.which('docker'):
        pytest.skip('docker command not found')
    status, output = subprocess.getstatusoutput('docker ps')
    if status == 0:
        pytest.skip("Docker appears to be running.")

    # expect "Cannot connect to the Docker daemon. Is the docker
    # daemon running on this host?'"
    assert 'Cannot connect to the Docker daemon' in output

    runner = DockerOOMMFRunner()
    with pytest.raises(RuntimeError):
        runner.call(argstr="+version")

@pytest.mark.travis
def test_no_runner_found():
    # Check that we get EnvironmentError if neither OOMMF nor docker are found
    if sys.platform == 'win32' and (
            ('Continuum' in sys.version) or ('Anaconda' in sys.version)):
        pytest.skip("Can't prevent finding oommmf in windows conda env")
    with testpath.modified_env({'OOMMFTCL': None}):
        with pytest.raises(EnvironmentError):
            get_oommf_runner(use_cache=False, docker_exe=nonexistant_docker,
                             oommf_exe=nonexistant_docker)
