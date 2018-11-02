import os
import sys
import time
import datetime
import logging
import shutil
import oommfc as oc
import subprocess as sp

log = logging.getLogger(__name__)
_cached_oommf_runner = None


class OOMMFRunner:
    """Base class for running OOMMF.

    Don't use this directly. Use get_oommf_runner() to pick a subclass
    of this class.

    """
    def call(self, argstr, need_stderr=False):
        now = datetime.datetime.now()
        timestamp = '{}/{:02d}/{:02d} {:02d}:{:02d}'.format(now.year,
                                                            now.month,
                                                            now.day,
                                                            now.hour,
                                                            now.minute)
        print('{}: Running OOMMF ({}) ... '.format(timestamp, argstr), end='')

        tic = time.time()
        res = self._call(argstr=argstr, need_stderr=need_stderr)
        self._kill()
        toc = time.time()
        seconds = '({:0.1f} s)'.format(toc - tic)
        print(seconds)

        if res.returncode is not 0:
            if sys.platform != 'win32':
                # Only on Linux and MacOS - on Windows we do not get
                # stderr and stdout.
                stderr = res.stderr.decode('utf-8', 'replace')
                stdout = res.stdout.decode('utf-8', 'replace')
                cmdstr = ' '.join(res.args)
                print('OOMMF error:')
                print('\tcommand: {}'.format(cmdstr))
                print('\tstdout: {}'.format(stdout))
                print('\tstderr: {}'.format(stderr))
                print('\n')
            raise RuntimeError('Error in OOMMF run.')

        return res

    def _call(self, argstr, need_stderr=False):
        # This method should be implemented in subclass.
        raise NotImplementedError

    def _kill(self, targets=('all',)):
        # This method should be implemented in subclass.
        raise NotImplementedError
    
    def version(self):
        res = self.call(argstr='+version', need_stderr=True)
        return res.stderr.decode('utf-8').split('oommf.tcl')[-1].strip()

    def platform(self):
        res = self.call(argstr='+platform', need_stderr=True)
        return res.stderr.decode('utf-8')

    
class TclOOMMFRunner(OOMMFRunner):
    """Using path to oommf.tcl.

    """
    def __init__(self, oommf_tcl):
        self.oommf_tcl = oommf_tcl  # a path to oommf.tcl

    def _call(self, argstr, need_stderr=False):
        cmd = ['tclsh', self.oommf_tcl, 'boxsi', '+fg',
               argstr, '-exitondone', '1']

        # Not clear why we cannot get stderr and stdout on
        # win32. Calls to OOMMF get stuck.
        stdout = stderr = sp.PIPE
        if sys.platform == 'win32' and not need_stderr:
            stdout = stderr = None

        return sp.run(cmd, stdout=stdout, stderr=stderr)

    def _kill(self, targets=['all']):
        sp.run(["tclsh", self.oommf_tcl, "killoommf"] + targets)


class ExeOOMMFRunner(OOMMFRunner):
    """Using oommf executable on $PATH.

    """
    def __init__(self, oommf_exe='oommf'):
        self.oommf_exe = oommf_exe

    def _call(self, argstr, need_stderr=False):
        # Here we might need stderr = stdot = None like in
        # TclOOMMFRunner for Windows.  This is not clear because we
        # never use ExeOOMMFRunner on Windows.

        cmd = [self.oommf_exe, 'boxsi', '+fg', argstr, '-exitondone', '1']
        return sp.run(cmd, stdout=sp.PIPE, stderr=sp.PIPE)

    def _kill(self, targets=['all']):
        sp.run([self.oommf_exe, "killoommf"] + targets)


class DockerOOMMFRunner(OOMMFRunner):
    """Run OOMMF in a docker container.

    """
    def __init__(self, docker_exe='docker', image='joommf/oommf'):
        self.image = image
        self.docker_exe = docker_exe

    def _call(self, argstr, need_stderr=False):
        cmd = [self.docker_exe, 'run', '-v', os.getcwd()+':/io',
               self.image, '/bin/bash', '-c',
               ('tclsh /usr/local/oommf/oommf/oommf.tcl boxsi '
                '+fg {} -exitondone 1').format(argstr)]
        return sp.run(cmd, stdout=sp.PIPE, stderr=sp.PIPE)

    def _kill(self, targets=('all',)):
        # There is no need to kill OOMMF when run inside docker.
        pass


def get_oommf_runner(use_cache=True, envvar='OOMMFTCL',
                     oommf_exe='oommf', docker_exe='docker'):
    """Find the best available way to run OOMMF.

    Returns an OOMMFRunner object, or raises EnvironmentError if no suitable
    method is found.

    Parameters
    ----------
    use_cache : bool
      The first call to this function will determine the best way to run OOMMF
      and cache it. Normally, subsequent calls will return the OOMMFRunner
      object from the cache. Setting this parameter to False will cause it to
      check for available methods again.
    envvar : str
      Name of the environment variable containing the path to oommf.tcl
    oommf_exe : str
      The name or path of the executable oommf command
    docker_exe : str
      The name or path of the docker command

    """
    global _cached_oommf_runner
    if use_cache and (_cached_oommf_runner is not None):
        return _cached_oommf_runner

    # Check for OOMMFTCL environment variable pointing to oommf.tcl.
    oommf_tcl = os.environ.get(envvar, None)
    if oommf_tcl is not None:
        cmd = ['tclsh', oommf_tcl, 'boxsi',
               '+fg', '+version', '-exitondone', '1']
        try:
            res = sp.run(cmd, stdout=sp.PIPE, stderr=sp.PIPE)
        except FileNotFoundError:
            log.warning('oommf.tcl was not found.')
        else:
            if res.returncode:
                log.warning('OOMMFTCL is set, but OOMMF could not be run.\n'
                            'stdout:\n{}\n'
                            'stderr:\n{}'.format(res.stdout, res.stderr))
            else:
                _cached_oommf_runner = TclOOMMFRunner(oommf_tcl)
                return _cached_oommf_runner

    # OOMMF is installed via conda and oommf.tcl is in opt/oommf
    # (Windows). This would probably also work on MacOS/Linux, but on
    # these operating systems, when installed via conda, we use
    # 'oommf' executable.
    if sys.platform == 'win32' and \
       os.path.isdir(os.path.join(sys.prefix, 'conda-meta')):
        oommf_tcl = os.path.join(sys.prefix, 'opt', 'oommf', 'oommf.tcl')
        if os.path.isfile(oommf_tcl):
            _cached_oommf_runner = TclOOMMFRunner(oommf_tcl)
            return _cached_oommf_runner

    # OOMMF available as an executable - in a conda env on Mac/Linux,
    # or oommf installed separately.
    oommf_exe = shutil.which(oommf_exe)
    if oommf_exe:
        _cached_oommf_runner = ExeOOMMFRunner(oommf_exe)
        return _cached_oommf_runner

    # Check for docker to run OOMMF in a docker image.
    cmd = [docker_exe, 'images']
    try:
        res = sp.run(cmd, stdout=sp.PIPE, stderr=sp.PIPE)
    except FileNotFoundError:
        log.warning('Docker was not found.')
    else:
        if res.returncode:
            log.warning('Error running docker\n'
                        'stdout:\n{}\n'
                        'stderr:\n{}'.format(res.stdout, res.stderr))
        else:
            _cached_oommf_runner = DockerOOMMFRunner(docker_exe=docker_exe,
                                                     image='joommf/oommf')
            return _cached_oommf_runner

    # If OOMMFRunner was not returned up to this point, we raise an
    # exception.
    raise EnvironmentError('Cannot find OOMMF.')


def status():
    """Run a macrospin example for 1 ps through oommfc and print the OOMMF
    status.

    """
    try:
        system = oc.examples.macrospin()
        td = oc.TimeDriver()
        td.drive(system, t=1e-12, n=1, overwrite=True)
        print('OOMMF found and running.')
        shutil.rmtree('example-macrospin')
        return 0
    except (EnvironmentError, RuntimeError):
        print("Cannot find OOMMF.")
        return 1

def overhead():
    """Run a macrospin example for 1 ps through oommfc and directly and
    return the difference in run times.

    Returns
    -------
    overhead : float
      The time difference (overhead) between running OOMMF though
      oommfc and directly

    """
    # Running OOMMF through oommfc.
    system = oc.examples.macrospin()
    td = oc.TimeDriver()
    oommfc_start = time.time()
    td.drive(system, t=1e-12, n=1, overwrite=True)
    oommfc_stop = time.time()
    oommfc_time = oommfc_stop - oommfc_start

    # Running OOMMF directly.
    oommf_runner = get_oommf_runner()
    mifpath = os.path.realpath(os.path.join('example-macrospin', 'drive-0',
                                            'example-macrospin.mif'))
    oommf_start = time.time()
    oommf_runner.call(mifpath)
    oommf_stop = time.time()
    oommf_time = oommf_stop - oommf_start
    shutil.rmtree('example-macrospin')

    return oommfc_time - oommf_time
