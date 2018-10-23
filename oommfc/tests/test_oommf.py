import os
import sys
import pytest
import shutil
import oommfc.oommf as oo


def check_runner(oommf_runner):
    dirname = os.path.join(os.path.dirname(__file__), 'test_files')
    os.chdir(dirname)
    argstr = 'test_oommf.mif'
    res = oommf_runner.call(argstr)
    version = oommf_runner.version()
    platform = oommf_runner.platform()

    assert isinstance(version, str)
    assert len(version) is not ''
    assert isinstance(platform, str)
    assert len(platform) is not ''
    assert res.returncode == 0

    files = os.listdir(dirname)
    for f in files:
        if f.endswith(".odt"):
            os.remove(os.path.join(dirname, f))
        elif f.endswith(".omf") and f.startswith("test_oommf-Oxs"):
            os.remove(os.path.join(dirname, f))


@pytest.mark.oommf
@pytest.mark.travis
def test_tcl_oommf_runner():
    """TclOOMMFRunner runs when OOMMFTCL environment variable is set.

    """
    oommf_tcl = os.environ.get('OOMMFTCL', None)
    oommf_runner = oo.TclOOMMFRunner(oommf_tcl)
    check_runner(oommf_runner)


@pytest.mark.oommf
@pytest.mark.travis
def test_exe_oommf_runner():
    """ExeOOMMFRunner runs when callable OOMMF exists ("oommf").

    """
    oommf_exe = "oommf"
    oommf_runner = oo.ExeOOMMFRunner(oommf_exe)
    check_runner(oommf_runner)


@pytest.mark.oommf
@pytest.mark.docker
def test_docker_oommf_runner():
    """DockerOOMMFRunner runs when docker is installed.

    """
    docker_exe = "docker"
    image = 'joommf/oommf'
    oommf_runner = oo.DockerOOMMFRunner(docker_exe, image)
    check_runner(oommf_runner)

    oommf_runner = oo.get_oommf_runner(use_cache=False,
                                       envvar='wrong_name',
                                       oommf_exe='wrong_name',
                                       docker_exe='docker')
    assert isinstance(oommf_runner, oo.DockerOOMMFRunner)


@pytest.mark.oommf
@pytest.mark.travis
def test_get_right_oommf_runner():
    # TclOOMMFRunner
    oommf_runner = oo.get_oommf_runner(use_cache=False,
                                       envvar='OOMMFTCL',
                                       oommf_exe='wrong_name',
                                       docker_exe='wrong_name')
    assert isinstance(oommf_runner, oo.TclOOMMFRunner)

    # ExeOOMMFRunner
    oommf_runner = oo.get_oommf_runner(use_cache=False,
                                       envvar='wrong_name',
                                       oommf_exe='oommf',
                                       docker_exe='wrong_name')
    assert isinstance(oommf_runner, oo.ExeOOMMFRunner)

    # OOMMF cannot be found on the system.
    with pytest.raises(EnvironmentError):
        oommf_runner = oo.get_oommf_runner(use_cache=False,
                                           envvar='wrong_name',
                                           oommf_exe='wrong_name',
                                           docker_exe='wrong_name')


@pytest.mark.oommf
@pytest.mark.travis
def test_cached_oommf_runner():
    oommf_runner = oo.get_oommf_runner(use_cache=False,
                                       envvar='wrong_name',
                                       oommf_exe='oommf',
                                       docker_exe='wrong_name')
    assert isinstance(oommf_runner, oo.ExeOOMMFRunner)

    oommf_runner = oo.get_oommf_runner(use_cache=True)
    assert isinstance(oommf_runner, oo.ExeOOMMFRunner)

    oommf_runner = oo.get_oommf_runner(use_cache=True,
                                       envvar='OOMMFTCL',
                                       oommf_exe='wrong_name',
                                       docker_exe='wrong_name')
    assert isinstance(oommf_runner, oo.ExeOOMMFRunner)


@pytest.mark.oommf
def test_get_oommf_runner():
    oommf_runner = oo.get_oommf_runner(use_cache=False)
    assert isinstance(oommf_runner, oo.OOMMFRunner)
    check_runner(oommf_runner)


@pytest.mark.oommf
def test_overhead():
    assert isinstance(oo.overhead(), float)


@pytest.mark.oommf
def test_status():
    assert oo.status() == 0


@pytest.mark.oommf
def test_runtimeerror():
    oommf_runner = oo.get_oommf_runner(use_cache=False)
    with pytest.raises(RuntimeError):
        oommf_runner.call("+wrong_argstr")
