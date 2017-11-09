import datetime
import logging
import os
import sys
import time
from shutil import which
from subprocess import run, PIPE

log = logging.getLogger(__name__)

class OOMMFRunner:
    """Base class for running OOMMF.
    
    Don't use this directly. You should normally use get_oommf_runner() to pick
    a subclass of this class.
    """

    def call(self, argstr):
        # print day and time at which we start calling OOMMF (useful
        # for longer runs)
        x = datetime.datetime.now()
        timestamp = "{}/{}/{} {}:{}".format(x.year, x.month, x.day,
                                            x.hour, x.minute)
        print("{}: Calling OOMMF ({}) ... ".format(timestamp, argstr), end='')

        # measure execution time of OOMMF
        tic = time.time()
        val = self._call(argstr=argstr)

        toc = time.time()
        seconds = "[{:0.1f}s]".format(toc - tic)
        print(seconds)

        # check exit code
        if val.returncode is not 0:
            stderr = val.stderr.decode('utf-8', 'replace')
            stdout = val.stdout.decode('utf-8', 'replace')
            cmdstr = " ".join(val.args)
            print("Error when executing:")
            print("\tcommand: {}".format(cmdstr))
            print("\tstdout: {}".format(stdout))
            print("\tstderr: {}".format(stderr))
            print("\n")
            raise RuntimeError("Some problem calling OOMMF.")

        return val

    def _call(self, argstr):
        # Implement in subclass
        raise NotImplementedError

    def version(self, where=None):
        p = self.call(argstr="+version")
        return p.stderr.text.split("oommf.tcl")[-1].strip()

    def platform(self, where=None):
        p = self.call(argstr="+platform")
        return p.stderr.text

class ScriptOOMMFRunner(OOMMFRunner):
    """Run OOMMF on this system, using an oommf executable on $PATH 
    """
    def __init__(self, script_name='oommf'):
        self.script_name = script_name

    def _oommf_cmd_tuple(self):
        return (self.script_name, )

    def _call(self, argstr):
        cmd = (self.script_name, "boxsi", "+fg", argstr, "-exitondone", "1")
        return run(cmd, stdout=PIPE, stderr=PIPE)

    def kill(self, targets=('all',)):
        run((self.script_name, "killoommf") + targets)


class NativeOOMMFRunner(ScriptOOMMFRunner):
    """Run OOMMF on this system, given a path to oommf.tcl
    
    This requires tclsh to be available.
    """
    def __init__(self, oommf_tcl_path):
        self.oommf_tcl_path = oommf_tcl_path

    def _call(self, argstr):
        cmd = ("tclsh", self.oommf_tcl_path, "boxsi", "+fg",
               argstr, "-exitondone", "1")
        return run(cmd, stdout=PIPE, stderr=PIPE)

    def kill(self, targets=('all',)):
        run(("tclsh", self.oommf_tcl_path, "killoommf") + targets)

class WindowsCondaOOMMFRunner(OOMMFRunner):
    """Run OOMMF in a conda env on Windows.
    
    tclsh is not available, so we call oxs.exe directly.
    """
    def __init__(self, oommf_root):
        self.oommf_root = oommf_root
    
    def _call(self, argstr):
        oxs_exe = os.path.join(self.oommf_root, 'app', 'oxs', 'windows-x86_64', 'oxs.exe')
        boxsi = os.path.join(self.oommf_root, 'app', 'oxs', 'boxsi.tcl')
        return run([oxs_exe, boxsi, argstr], stdout=PIPE, stderr=PIPE)
    
    def kill(self, targets=('all',)):
        pass


class DockerOOMMFRunner(OOMMFRunner):
    """Run OOMMF inside a docker image"""
    def __init__(self, image="joommf/oommf", docker_exe='docker'):
        self.image = image
        self.docker_exe = docker_exe

    def _call(self, argstr):
        run([self.docker_exe, "pull", self.image])
        cmd = [self.docker_exe, 'run', '-v', os.getcwd()+':/io', self.image,
               "/bin/bash", "-c",
               ("tclsh /usr/local/oommf/oommf/oommf.tcl boxsi +fg {} "
                "-exitondone 1").format(argstr)]
        return run(cmd, stdout=PIPE, stderr=PIPE)

    def kill(self):
        pass # Does this need to do anything?

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
        cmd = ("tclsh", oommf_tcl_path, "boxsi",
               "+fg", "+version", "-exitondone", "1")
        try:
            res = run(cmd, stdout=PIPE, stderr=PIPE)
        except FileNotFoundError:
            log.warning("tclsh was not found")
        else:
            if res.returncode:
                log.warning("OOMMFTCL is set, but there was a problem running oommf.\n"
                            "stdout:\n{}\n\n"
                            "stderr:\n{}".format(res.stdout, res.stderr))
            else:
                _cached_oommf_runner = NativeOOMMFRunner(oommf_tcl_path)
                return _cached_oommf_runner

    if sys.platform == 'win32' and \
            os.path.isdir(os.path.join(sys.prefix, 'conda-meta')):
        # In a conda env on Windows
        oommf_root = os.path.join(sys.prefix, 'opt', 'oommf')
        if os.path.isdir(oommf_root):
            _cached_oommf_runner = WindowsCondaOOMMFRunner(oommf_root)
            return _cached_oommf_runner
               
    oommf_exe_path = which(oommf_exe)
    if oommf_exe_path:
        _cached_oommf_runner = ScriptOOMMFRunner(oommf_exe_path)
        return _cached_oommf_runner

    # Check for docker to run OOMMF in a docker image
    cmd = (docker_exe, "images")
    try:
        res = run(cmd, stdout=PIPE, stderr=PIPE)
    except FileNotFoundError:
        log.warning("docker was not found")
    else:
        if res.returncode:
            log.warning("Error running docker\n"
                "stdout:\n{}\n\n"
                "stderr:\n{}".format(res.stdout, res.stderr))
        else:
            _cached_oommf_runner = DockerOOMMFRunner(image="joommf/oommf")
            return _cached_oommf_runner

    # Raise exception if we can't find a way to run OOMMF
    raise EnvironmentError("Could not run $OOMMFTCL or docker.")
