import os
import sys
import time
import datetime
import logging
import subprocess as sp
from shutil import which

log = logging.getLogger(__name__)
    

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
        toc = time.time()
        seconds = '({:0.1f} s)'.format(toc - tic)
        print(seconds)

        if res.returncode is not 0:
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

    def version(self):
        res = self.call(argstr='+version', need_stderr=True)
        return res.stderr.decode('utf-8').split('oommf.tcl')[-1].strip()

    def platform(self):
        res = self.call(argstr='+platform', need_stderr=True)
        return res.stderr.decode('utf-8')


class TclOOMMFRunner(ScriptOOMMFRunner):
    """Using path to oommf.tcl

    """
    def __init__(self, oommf_tcl_path):
        self.oommf_tcl_path = oommf_tcl_path

    def _call(self, argstr, need_stderr=False):
        cmd = ['tclsh', self.oommf_tcl_path, 'boxsi', '+fg',
               argstr, '-exitondone', '1']

        # Not clear why we cannot get stderr and stdout on
        # win32. Calls to OOMMF get stuck.
        stdout = stderr = sp.PIPE
        if sys.platform == 'win32' and not need_stderr:
            stdout = stderr = None

        return sp.run(cmd, stdout=stdout, stderr=stderr)


class ScriptOOMMFRunner(OOMMFRunner):
    """Using oommf executable on $PATH.

    """
    def __init__(self, script_name='oommf'):
        self.script_name = script_name

    def _call(self, argstr, need_stderr=False):
        cmd = [self.script_name, 'boxsi', '+fg', argstr, '-exitondone', '1']
        return sp.run(cmd, stdout=sp.PIPE, stderr=sp.PIPE)


class DockerOOMMFRunner(OOMMFRunner):
    """Run OOMMF in a docker container.

    """
    def __init__(self, docker_image='joommf/oommf', docker_exe='docker'):
        self.docker_image = docker_image
        self.docker_exe = docker_exe

    def _call(self, argstr, need_stderr=False):
        cmd = [self.docker_exe, 'run', '-v', os.getcwd()+':/io',
               self.docker_image, '/bin/bash', '-c',
               ('tclsh /usr/local/oommf/oommf/oommf.tcl boxsi +fg {} '
                '-exitondone 1').format(argstr)]
        return sp.run(cmd, stdout=sp.PIPE, stderr=sp.PIPE)


_cached_oommf_runner = None

def get_oommf_runner(use_cache=True, docker_exe='docker', oommf_exe='oommf'):
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
    docker_exe : str
      The name or path of the docker command.
    """
    global _cached_oommf_runner
    if use_cache and (_cached_oommf_runner is not None):
        return _cached_oommf_runner

    # Check for $OOMMFTCL environment variable pointing to native OOMMF
    oommf_tcl_path = os.environ.get('OOMMFTCL', None)
    if oommf_tcl_path:
        cmd = ('tclsh', oommf_tcl_path, 'boxsi',
               '+fg', '+version', '-exitondone', '1')
        try:
            res = sp.run(cmd, stdout=sp.PIPE, stderr=sp.PIPE)
        except FileNotFoundError:
            log.warning('tclsh was not found')
        else:
            if res.returncode:
                log.warning('OOMMFTCL is set, but there was a problem running oommf.\n'
                            'stdout:\n{}\n\n'
                            'stderr:\n{}'.format(res.stdout, res.stderr))
            else:
                _cached_oommf_runner = TclOOMMFRunner(oommf_tcl_path)
                return _cached_oommf_runner

    if sys.platform == 'win32' and \
            os.path.isdir(os.path.join(sys.prefix, 'conda-meta')):
        # In a conda env on Windows, would probably also work on Mac/Linux
        oommf_tcl = os.path.join(sys.prefix, 'opt', 'oommf', 'oommf.tcl')
        if os.path.isfile(oommf_tcl):
            _cached_oommf_runner = TclOOMMFRunner(oommf_tcl)
            return _cached_oommf_runner

	# 'oommf' available as a command - in a conda env on Mac/Linux, or oommf installed separately
    oommf_exe_path = which(oommf_exe)
    if oommf_exe_path:
        _cached_oommf_runner = ScriptOOMMFRunner(oommf_exe_path)
        return _cached_oommf_runner

    # Check for docker to run OOMMF in a docker image
    cmd = (docker_exe, 'images')
    try:
        res = sp.run(cmd, stdout=sp.PIPE, stderr=sp.PIPE)
    except FileNotFoundError:
        log.warning('docker was not found')
    else:
        if res.returncode:
            log.warning('Error running docker\n'
                'stdout:\n{}\n\n'
                'stderr:\n{}'.format(res.stdout, res.stderr))
        else:
            _cached_oommf_runner = DockerOOMMFRunner(image='joommf/oommf')
            return _cached_oommf_runner

    # Raise exception if we can't find a way to run OOMMF
    raise EnvironmentError('Could not run $OOMMFTCL or docker.')
