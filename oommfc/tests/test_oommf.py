import os
import sys
import pytest
import oommfc as oc
import oommfc.oommf as oo
import micromagneticmodel as mm


@pytest.fixture
def reset_runner():
    oc.runner = oo.Runner()


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


def test_tcl_oommf_runner(reset_runner):
    # assumes that conda is used to install oommf
    oommf_tcl = os.path.join(sys.prefix, 'opt', 'oommf', 'oommf.tcl')
    runner = oo.TclOOMMFRunner(oommf_tcl)
    assert isinstance(runner.errors(), str)
    check_runner(runner)

    # via runner object
    oc.runner.oommf_exe = 'wrong_name'
    oc.runner.docker_exe = 'wrong_name'
    os.environ.setdefault('OOMMFTCL', oommf_tcl)
    oc.runner.autoselect_runner()
    runner = oc.runner.runner
    assert isinstance(runner, oo.TclOOMMFRunner)
    check_runner(runner)


def test_exe_oommf_runner(reset_runner):
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


@pytest.mark.skip(
    'OOMMF inside docker cannot be tested on CI [non-default user].')
def test_docker_oommf_runner(reset_runner):
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


def test_get_oommf_runner(reset_runner):
    oc.runner.autoselect_runner()
    oommf_runner = oc.runner.runner
    assert isinstance(oommf_runner, oo.OOMMFRunner)
    check_runner(oommf_runner)


def test_missing_oommf(reset_runner):
    oc.runner.envvar = 'wrong_name'
    oc.runner.oommf_exe = 'wrong_name'
    oc.runner.docker_exe = 'wrong_name'
    with pytest.raises(EnvironmentError):
        oc.runner.runner


def test_get_cached_runner(reset_runner):
    # ensure ExeOOMMFRunner
    oc.runner.envvar = 'wrong_name'
    oc.runner.autoselect_runner()
    runner = oc.runner.runner
    assert isinstance(runner, oo.ExeOOMMFRunner)
    check_runner(runner)

    oc.runner.oommf_exe = 'wrong_name'
    runner = oc.runner.runner  # cached
    assert isinstance(runner, oo.ExeOOMMFRunner)
    check_runner(runner)

    oc.runner.cache_runner = False
    runner = oc.runner.runner
    assert isinstance(runner, oo.DockerOOMMFRunner)
    # docker runner cannot be executed on CI
    # check_runner(runner)

    # assumes that conda is used to install oommf
    oommf_tcl = os.path.join(sys.prefix, 'opt', 'oommf', 'oommf.tcl')
    os.environ.setdefault('OOMMFTCL', oommf_tcl)
    oc.runner.envvar = 'OOMMFTCL'
    runner = oc.runner.runner
    assert isinstance(runner, oo.TclOOMMFRunner)
    check_runner(runner)


def test_set_oommf_runner(reset_runner):
    # assumes that conda is used to install oommf
    oommf_tcl = os.path.join(sys.prefix, 'opt', 'oommf', 'oommf.tcl')
    oc.runner.runner = oo.TclOOMMFRunner(oommf_tcl)
    assert isinstance(oc.runner.runner, oo.TclOOMMFRunner)

    oc.runner.runner = oo.ExeOOMMFRunner()
    assert isinstance(oc.runner.runner, oo.ExeOOMMFRunner)

    oc.runner.runner = oo.DockerOOMMFRunner()
    assert isinstance(oc.runner.runner, oo.DockerOOMMFRunner)


def test_status(reset_runner):
    assert oc.runner.runner.status == 0


def test_overhead(reset_runner):
    assert isinstance(oo.overhead(), float)


def test_wrong_command(reset_runner):
    oc.runner.autoselect_runner()
    oommf_runner = oc.runner.runner
    with pytest.raises(RuntimeError):
        oommf_runner.call('+wrong_argstr')


def test_choose_runner(reset_runner):
    system = mm.examples.macrospin()

    md = oc.MinDriver()
    runner = oc.oommf.ExeOOMMFRunner()
    md.drive(system, runner=runner)


def test_silent(capsys, reset_runner):
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
