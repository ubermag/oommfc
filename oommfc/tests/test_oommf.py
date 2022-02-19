import os
import sys
import pytest
import shutil
import oommfc as oc
import oommfc.oommf as oo
import micromagneticmodel as mm


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


@pytest.mark.skip(reason='Temporary')
def test_tcl_oommf_runner():
    # TclOOMMFRunner runs when OOMMFTCL environment variable is set. On
    # TravisCI OOMMFTCL environment variable is set inside oommf/oommf docker
    # image.
    oommf_tcl = os.environ.get('OOMMFTCL', None)
    runner = oo.TclOOMMFRunner(oommf_tcl)
    check_runner(runner)
    assert isinstance(runner.errors(), str)


@pytest.mark.skip(reason='Temporary')
def test_exe_oommf_runner():
    # ExeOOMMFRunner runs when callable OOMMF exists ('oommf'). On TravisCI
    # oommf is an executable inside oommf/oommf docker image.
    oommf_exe = 'oommf'
    runner = oo.ExeOOMMFRunner(oommf_exe)
    check_runner(runner)
    with pytest.raises(EnvironmentError):
        # On travis oommf compiled from source is used.
        errors = runner.errors()


@pytest.mark.skip(reason='Temporary')
def test_docker_oommf_runner():
    # DockerOOMMFRunner runs when docker is installed. This test does not run
    # on host or TravisCI. It can be run using make test-docker on host if
    # docker is installed.
    docker_exe = 'docker'
    image = 'oommf/oommf'
    runner = oo.DockerOOMMFRunner(docker_exe, image)
    check_runner(runner)

    # An additional check of getting OOMMF runner when docker is installed.
    runner = oo.get_oommf_runner(use_cache=False,
                                 envvar='wrong_name',
                                 oommf_exe='wrong_name',
                                 docker_exe='docker')
    assert isinstance(runner, oo.DockerOOMMFRunner)
    check_runner(runner)

    with pytest.raises(EnvironmentError):
        errors = runner.errors()


@pytest.mark.skip(reason='Temporary')
def test_get_oommf_runner():
    # TclOOMMFRunner
    oommf_runner = oo.get_oommf_runner(use_cache=False,
                                       envvar='OOMMFTCL',
                                       oommf_exe='wrong_name',
                                       docker_exe='wrong_name')
    assert isinstance(oommf_runner, oo.TclOOMMFRunner)
    check_runner(oommf_runner)

    # ExeOOMMFRunner
    oommf_runner = oo.get_oommf_runner(use_cache=False,
                                       envvar='wrong_name',
                                       oommf_exe='oommf',
                                       docker_exe='wrong_name')
    assert isinstance(oommf_runner, oo.ExeOOMMFRunner)
    check_runner(oommf_runner)

    # OOMMF cannot be found on the system.
    with pytest.raises(EnvironmentError):
        oommf_runner = oo.get_oommf_runner(use_cache=False,
                                           envvar='wrong_name',
                                           oommf_exe='wrong_name',
                                           docker_exe='wrong_name')

    # Test cached OOMMFRunner.
    oommf_runner = oo.get_oommf_runner(use_cache=False,
                                       envvar='wrong_name',
                                       oommf_exe='oommf',
                                       docker_exe='wrong_name')
    assert isinstance(oommf_runner, oo.ExeOOMMFRunner)
    check_runner(oommf_runner)

    oommf_runner = oo.get_oommf_runner(use_cache=True)
    assert isinstance(oommf_runner, oo.ExeOOMMFRunner)
    check_runner(oommf_runner)

    oommf_runner = oo.get_oommf_runner(use_cache=True,
                                       envvar='OOMMFTCL',
                                       oommf_exe='wrong_name',
                                       docker_exe='wrong_name')
    assert isinstance(oommf_runner, oo.ExeOOMMFRunner)
    check_runner(oommf_runner)


def test_get_oommf_runner():
    # This is a shorter version of the previous test for testing on host.
    oc.runner.autoselect_runner()
    oommf_runner = oc.runner.runner
    assert isinstance(oommf_runner, oo.OOMMFRunner)
    check_runner(oommf_runner)


@pytest.mark.skip(reason='We need to think about how to test this properly.')
def test_set_oommf_runner():
    oc.runner.runner = oo.TclOOMMFRunner()
    assert isinstance(oc.runner.runner, oo.TclOOMMFRunner)

    oc.runner.runner = oo.ExeOOMMFRunner()
    assert isinstance(oc.runner.runner, oo.ExeOOMMFRunner)

    oc.runner.runner = oo.DockerOOMMFRunner()
    assert isinstance(oc.runner.runner, oo.DockerOOMMFRunner)


@pytest.mark.skip(reason='Temporary')
def test_status():
    assert oo.status() == 0


def test_overhead():
    assert isinstance(oo.overhead(), float)


def test_runtimeerror():
    oc.runner.autoselect_runner()
    oommf_runner = oc.runner.runner
    with pytest.raises(RuntimeError):
        oommf_runner.call('+wrong_argstr')


@pytest.mark.skip(reason='Temporary')
def test_choose_runner():
    system = mm.examples.macrospin()

    md = oc.MinDriver()
    runner = oc.oommf.TclOOMMFRunner(oommf_tcl=os.environ.get('OOMMFTCL',
                                                              None))
    md.drive(system, runner=runner)

    runner = oc.oommf.ExeOOMMFRunner(oommf_exe='oommf')
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
