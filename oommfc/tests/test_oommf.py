import os
import pytest
import oommfc.oommf as oo


def check_runner(oommf_runner):
    argstr = os.path.join('test_files', 'test_oommf.mif')
    res = oommf_runner.call(argstr)
    version = oommf_runner.version()
    platform = oommf_runner.platform()
    
    assert isinstance(version, str)
    assert len(version) is not ''
    assert isinstance(platform, str)
    assert len(platform) is not ''
    assert res.returncode == 0


@pytest.mark.travis
def test_tcl_oommf_runner():
    """TclOOMMFRunner runs when OOMMFTCL environment variable is set.

    """
    oommf_tcl = os.environ.get('OOMMFTCL', None)
    oommf_runner = oo.oommf.TclOOMMFRunner(oommf_tcl)
    check_runner(oommf_runner)


@pytest.mark.travis
def test_exe_oommf_runner():
    """ExeOOMMFRunner runs when callable OOMMF exists ("oommf").

    """
    oommf_exe = "oommf"
    oommf_runner = oo.oommf.ExeOOMMFRunner(oommf_exe)
    check_runner(oommf_runner)


@pytest.mark.travis
def test_docker_oommf_runner():
    """DockerOOMMFRunner runs when docker is installed.

    """
    docker_exe = "docker"
    image = 'joommf/oommf'
    oommf_runner = oo.oommf.DockerOOMMFRunner(docker_exe, image)
    check_runner(oommf_runner)


@pytest.mark.travis
def test_get_right_oommf_runner():
    # TclOOMMFRunner
    oommf_runner = oo.oommf.get_oommf_runner(use_cache=False,
                                             envvar='OOMMFTCL',
                                             oommf_exe='wrong_name',
                                             docker_exe='wrong_name')
    assert isinstance(oommf_runner, oo.oommf.TclOOMMFRunner)

    # ExeOOMMFRunner
    oommf_runner = oo.oommf.get_oommf_runner(use_cache=False,
                                             envvar='wrong_name',
                                             oommf_exe='oommf',
                                             docker_exe='wrong_name')
    assert isinstance(oommf_runner, oo.oommf.ExeOOMMFRunner)

    # DockerOOMMFRunner
    oommf_runner = oo.oommf.get_oommf_runner(use_cache=False,
                                             envvar='wrong_name',
                                             oommf_exe='wrong_name',
                                             docker_exe='docker')
    assert isinstance(oommf_runner, oo.oommf.DockerOOMMFRunner)


def test_get_oommf_runner():
    oommf_runner = oo.oommf.get_oommf_runner()
    check_runner(oommf_runner)
