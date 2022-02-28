import contextlib
import os
import re
import sys

import micromagneticmodel as mm
import pytest

import oommfc as oc
import oommfc.oommf as oo


def check_runner(runner):
    # Testing OOMMF on a mif file to make it independent of oommfc.
    dirname = os.path.join(os.path.dirname(__file__), 'test_sample')
    os.chdir(dirname)
    argstr = 'test_oommf.mif'
    res = runner.call(argstr)
    version = runner.version
    platform = runner.platform

    assert isinstance(version, str)
    assert len(version) > 0
    assert isinstance(platform, str)
    assert len(platform) > 0
    assert res.returncode == 0

    # Cleanup created files.
    for f in os.listdir(dirname):
        if f.endswith('.odt'):
            os.remove(os.path.join(dirname, f))
        elif f.endswith('.omf') and f.startswith('test_oommf-Oxs'):
            os.remove(os.path.join(dirname, f))


@pytest.fixture(autouse=True)
def reset_runner():
    oc.runner = oo.Runner()


def oommf_tcl_path():
    oommf_tcl = os.environ.get('OOMMFTCL')
    if oommf_tcl:
        return oommf_tcl
    # oommf installed via conda
    oommf_tcl = os.path.join(sys.prefix, 'opt', 'oommf', 'oommf.tcl')
    if os.path.exists(oommf_tcl):
        return oommf_tcl
    return None


@pytest.mark.skipif(
    oommf_tcl_path() is None,
    reason='Location of oommf.tcl unknown.')
def test_tcl_oommf_runner(monkeypatch):
    runner = oo.TclOOMMFRunner(oommf_tcl_path())
    assert isinstance(runner.errors(), str)
    check_runner(runner)

    # via runner object
    oc.runner.oommf_exe = 'wrong_name'
    oc.runner.docker_exe = 'wrong_name'
    monkeypatch.setenv('OOMMFTCL', oommf_tcl_path())
    oc.runner.autoselect_runner()
    runner = oc.runner.runner
    assert isinstance(runner, oo.TclOOMMFRunner)
    check_runner(runner)
    assert re.match(r'^TclOOMMFRunner\(.*\)$', repr(runner))


def test_exe_oommf_runner():
    runner = oo.ExeOOMMFRunner()
    check_runner(runner)
    assert isinstance(runner.errors(), str)

    # via runner object
    oc.runner.envvar = 'wrong_name'
    oc.runner.docker_exe = 'wrong_name'
    oc.runner.autoselect_runner()
    runner = oc.runner.runner
    assert isinstance(runner, oo.ExeOOMMFRunner)
    check_runner(runner)
    assert re.match(r'^ExeOOMMFRunner\(.*\)$', repr(runner))


@pytest.mark.skip(
    'OOMMF inside docker cannot be tested on CI [non-default user].')
def test_docker_oommf_runner():
    runner = oo.DockerOOMMFRunner()
    check_runner(runner)
    assert isinstance(runner, oo.DockerOOMMFRunner)
    # errors cannot be retrieved from docker image
    with pytest.raises(EnvironmentError):
        runner.errors()

    # via runner object
    oc.runner.envvar = 'wrong_name'
    oc.runner.oommf_exe = 'wrong_name'
    oc.runner.autoselect_runner()
    runner = oc.runner.runner
    assert isinstance(runner, oo.DockerOOMMFRunner)
    check_runner(runner)


def test_docker_no_oommf_run():
    runner = oo.DockerOOMMFRunner()
    assert isinstance(runner, oo.DockerOOMMFRunner)
    assert re.match(r'^DockerOOMMFRunner\(docker_exe=.*, image=.*\)$',
                    repr(runner))
    with pytest.raises(EnvironmentError):
        runner.errors()


def test_get_oommf_runner(monkeypatch):
    monkeypatch.setenv('OOMMFTCL', 'wrong_name')  # wrong environment variable
    oc.runner.autoselect_runner()
    oommf_runner = oc.runner.runner
    assert isinstance(oommf_runner, oo.ExeOOMMFRunner)
    check_runner(oommf_runner)


def test_missing_oommf():
    oc.runner.envvar = 'wrong_name'
    oc.runner.oommf_exe = 'wrong_name'
    oc.runner.docker_exe = 'wrong_name'
    with pytest.raises(EnvironmentError):
        oc.runner.runner


def test_get_cached_runner(reset_runner, monkeypatch):
    # ensure ExeOOMMFRunner
    oc.runner.envvar = 'wrong_name'
    runner = oc.runner.runner
    assert isinstance(runner, oo.ExeOOMMFRunner)
    check_runner(runner)

    oc.runner.oommf_exe = 'wrong_name'
    runner = oc.runner.runner  # cached
    assert isinstance(runner, oo.ExeOOMMFRunner)
    check_runner(runner)

    oc.runner.cache_runner = False
    oc.runner.docker_exe = 'wrong_name'  # ensure that we do not find docker
    with pytest.raises(EnvironmentError):
        oc.runner.runner

    oc.runner.envvar = 'OOMMFTCL'
    if oommf_tcl_path():
        expectation = contextlib.nullcontext()
        monkeypatch.setenv('OOMMFTCL', oommf_tcl_path())
    else:
        expectation = pytest.raises(EnvironmentError)
    with expectation:
        runner = oc.runner.runner
        assert isinstance(runner, oo.TclOOMMFRunner)
        check_runner(runner)


@pytest.mark.skipif(
    oommf_tcl_path() is None,
    reason='Location of oommf.tcl unknown.')
def test_set_tcl_oommf_runner():
    # assumes that conda is used to install oommf
    oc.runner.runner = oo.TclOOMMFRunner(oommf_tcl_path())
    assert isinstance(oc.runner.runner, oo.TclOOMMFRunner)


def test_set_exe_oommf_runner():
    oc.runner.runner = oo.ExeOOMMFRunner()
    assert isinstance(oc.runner.runner, oo.ExeOOMMFRunner)


@pytest.mark.skip(
    'OOMMF inside docker cannot be tested on CI [non-default user].')
def test_set_docker_oommf_runner():
    # Before a new runner is set we test if it can be used
    oc.runner.runner = oo.DockerOOMMFRunner()
    assert isinstance(oc.runner.runner, oo.DockerOOMMFRunner)


def test_runner_repr():
    assert repr(oc.runner) == 'OOMMF runner: UNSET\nrunner is cached: True'
    oc.runner.autoselect_runner()
    assert re.match(r'^OOMMF runner: (Tcl|Exe|Docker)OOMMFRunner.+',
                    repr(oc.runner))


def test_set_invalid_runner():
    with pytest.raises(ValueError):
        oc.runner.runner = oo.TclOOMMFRunner('wrong_name')


def test_status():
    assert oc.runner.runner.status == 0
    oc.runner._runner = oo.TclOOMMFRunner('wrong_name')  # force wrong runner
    assert oc.runner.runner.status == 1
    oc.runner.autoselect_runner()  # let oommfc find a correct runner
    assert oc.runner.runner.status == 0


def test_overhead():
    assert isinstance(oo.overhead(), float)


def test_wrong_command():
    oc.runner.autoselect_runner()
    oommf_runner = oc.runner.runner
    with pytest.raises(RuntimeError):
        oommf_runner.call('+wrong_argstr')


def test_choose_runner():
    system = mm.examples.macrospin()

    md = oc.MinDriver()
    runner = oc.oommf.ExeOOMMFRunner()
    md.drive(system, runner=runner)


def test_silent(capsys):
    md = oc.MinDriver()
    md.drive(mm.examples.macrospin())
    captured = capsys.readouterr()
    assert 'Running OOMMF' in captured.out

    md.drive(mm.examples.macrospin(), verbose=2)
    captured = capsys.readouterr()
    assert 'Running OOMMF' in captured.out

    md.drive(mm.examples.macrospin(), verbose=0)
    captured = capsys.readouterr()
    assert captured.out == ''
    assert captured.err == ''
