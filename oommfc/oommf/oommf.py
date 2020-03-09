import os
import abc
import sys
import time
import datetime
import logging
import shutil
import oommfc as oc
import subprocess as sp
import ubermagutil as uu
import micromagneticmodel as mm

log = logging.getLogger(__name__)
_cached_oommf_runner = None


class OOMMFRunner(metaclass=abc.ABCMeta):
    """Abstract class for running OOMMF.

    """
    def call(self, argstr, need_stderr=False):
        """Calls OOMMF by passing ``argstr`` to OOMMF.

        Parameters
        ----------
        argstr : str

            Argument string passed to OOMMF.

        need_stderr : bool

            If ``need_stderr=True``, standard error is captured. Defaults to
            ``False``.

        Raises
        ------
        RuntimeError

            If an error occured.

        Returns
        -------
        int

            When the OOMMF run was successful, ``0`` is returned.

        Examples
        --------
        1. Getting OOMMF runner automatically and calling it.

        >>> import oommfc as oc
        ...
        >>> runner = oc.oommf.get_oommf_runner()
        >>> runner.call(argstr='+version')
        Running OOMMF...
        CompletedProcess(...)

        """
        now = datetime.datetime.now()
        timestamp = '{}/{:02d}/{:02d} {:02d}:{:02d}'.format(now.year,
                                                            now.month,
                                                            now.day,
                                                            now.hour,
                                                            now.minute)
        print(f'Running OOMMF ({self.__class__.__name__}) [{timestamp}]... ',
              end='')

        tic = time.time()
        res = self._call(argstr=argstr, need_stderr=need_stderr)
        self._kill()  # kill OOMMF (mostly needed on Windows)
        toc = time.time()
        seconds = '({:0.1f} s)'.format(toc - tic)
        print(seconds)  # append seconds to the previous print.

        if res.returncode != 0:
            if sys.platform != 'win32':
                # Only on Linux and MacOS - on Windows we do not get stderr and
                # stdout.
                stderr = res.stderr.decode('utf-8', 'replace')
                stdout = res.stdout.decode('utf-8', 'replace')
                cmdstr = ' '.join(res.args)
                print('OOMMF error:')
                print(f'\tcommand: {cmdstr}')
                print(f'\tstdout: {cmdstr}')
                print(f'\tstderr: {stderr}')
                print('\n')
            raise RuntimeError('Error in OOMMF run.')

        return res

    @abc.abstractmethod
    def _call(self, argstr, need_stderr=False):
        """This method should be implemented in subclass.

        """
        pass  # pragma: no cover

    @abc.abstractmethod
    def _kill(self, targets=('all',)):
        """This method should be implemented in subclass.

        """
        pass  # pragma: no cover

    @abc.abstractmethod
    def errors(self):
        """Returns the content of ``boxsii.errors`` OOMMF file.

        Returns
        -------
        str

            ``boxsii.errors`` OOMMF file.

        """
        pass  # pragma: no cover

    def version(self):
        """Returns the OOMMF version.

        Returns
        -------
        str

            OOMMF version.

        Examples
        --------
        1. Getting OOMMF version.

        >>> import oommfc as oc
        ...
        >>> runner = oc.oommf.get_oommf_runner()
        >>> runner.version()
        Running OOMMF...
        '...'

        """
        res = self.call(argstr='+version', need_stderr=True)
        return res.stderr.decode('utf-8').split('oommf.tcl')[-1].strip()

    def platform(self):
        """Returns platform seen by OOMMF.

        Returns
        -------
        str

            Platform.

        Examples
        --------
        1. Getting platform.

        >>> import oommfc as oc
        ...
        >>> runner = oc.oommf.get_oommf_runner()
        >>> runner.platform()
        Running OOMMF...
        '...'

        """
        res = self.call(argstr='+platform', need_stderr=True)
        return res.stderr.decode('utf-8')


@uu.inherit_docs
class TclOOMMFRunner(OOMMFRunner):
    """OOMMF runner using path to ``oommf.tcl``.

    Parameters
    ----------
    oommf_tcl: str

        Path to ``oommf.tcl``file.

    """
    def __init__(self, oommf_tcl):
        self.oommf_tcl = oommf_tcl  # a path to oommf.tcl

    def _call(self, argstr, need_stderr=False):
        cmd = ['tclsh', self.oommf_tcl, 'boxsi', '+fg',
               argstr, '-exitondone', '1']

        # Not clear why we cannot get stderr and stdout on win32. Calls to
        # OOMMF get stuck.
        stdout = stderr = sp.PIPE
        if sys.platform == 'win32' and not need_stderr:
            stdout = stderr = None  # pragma: no cover

        return sp.run(cmd, stdout=stdout, stderr=stderr)

    def _kill(self, targets=['all']):
        sp.run(['tclsh', self.oommf_tcl, 'killoommf'] + targets)

    def errors(self):
        errors_file = os.path.join(os.path.dirname(self.oommf_tcl),
                                   'boxsi.errors')
        with open(errors_file, 'r') as f:
            errors = f.read()

        return errors


@uu.inherit_docs
class ExeOOMMFRunner(OOMMFRunner):
    """OOMMF runner using OOMMF executable, which can be found on $PATH.

    Parameters
    ----------
    oommf_exe: str

        Name of the OOMMF executable. Defaults to ``oommf``.

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
        sp.run([self.oommf_exe, 'killoommf'] + targets)

    def errors(self):
        try:
            errors_file = os.path.join(
                os.path.dirname(shutil.which(self.oommf_exe)),
                '..', 'opt', 'oommf', 'boxsi.errors')
            with open(errors_file, 'r') as f:
                errors = f.read()
            return errors

        except FileNotFoundError:
            msg = 'boxsi.errors cannot be retrieved.'
            raise EnvironmentError(msg)


@uu.inherit_docs
class DockerOOMMFRunner(OOMMFRunner):
    """OOMMF runner using Docker.

    Parameters
    ----------
    docker_exe: str

        Docker executable. Defaults to ``docker``.

    image: str

        Docker image on DockerHub. Defaults to ``ubermag/oommf``.

    """
    def __init__(self, docker_exe='docker', image='ubermag/oommf'):
        self.docker_exe = docker_exe
        self.image = image

    def _call(self, argstr, need_stderr=False):
        cmd = [self.docker_exe, 'run', '-v', os.getcwd()+':/io',
               self.image, '/bin/bash', '-c',
               ('tclsh /usr/local/oommf/oommf/oommf.tcl boxsi '
                '+fg {} -exitondone 1').format(argstr)]
        return sp.run(cmd, stdout=sp.PIPE, stderr=sp.PIPE)

    def _kill(self, targets=('all',)):
        # There is no need to kill OOMMF when run inside docker.
        pass

    def errors(self):
        msg = 'boxsi.errors cannot be retrieved from Docker container.'
        raise EnvironmentError(msg)


def get_oommf_runner(use_cache=True, envvar='OOMMFTCL',
                     oommf_exe='oommf', docker_exe='docker'):
    """Find the best available way to run OOMMF.

    Returns an ``oommfc.oommf.OOMMFRunner`` object, or raises
    ``EnvironmentError`` if no suitable method is found.

    Parameters
    ----------
    use_cache : bool

      The first call to this function will determine the best way to run OOMMF
      and cache it. Normally, subsequent calls will return the ``OOMMFRunner``
      object from the cache. Setting this parameter to ``False`` will cause it
      to check for available methods again. Defaults to ``True``.

    envvar : str

      Name of the environment variable containing the path to ``oommf.tcl``.
      Defaults to ``'OOMMFTCL'``.

    oommf_exe : str

      The name or path of the executable ``oommf`` command. Defaults to
      ``'oommf'``.

    docker_exe : str

      The name or path of the docker command. Defaults to ``'docker'``.

    Returns
    -------
    oommfc.oommf.OOMMFRunner

        An OOMMF runner.

    Raises
    ------
    EnvironmentError

        If no OOMMF can be found on host.

    Examples
    --------
    1. Getting OOMMF Runner.

    >>> import oommfc as oc
    ...
    >>> runner = oc.oommf.get_oommf_runner()
    >>> isinstance(runner, oc.oommf.OOMMFRunner)
    True

    """
    global _cached_oommf_runner
    if use_cache and (_cached_oommf_runner is not None):
        return _cached_oommf_runner

    # Check for the OOMMFTCL environment variable pointing to oommf.tcl.
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
                            f'stdout:\n{res.stdout}\n'
                            f'stderr:\n{res.stderr}')
            else:
                _cached_oommf_runner = TclOOMMFRunner(oommf_tcl)
                return _cached_oommf_runner

    # OOMMF is installed via conda and oommf.tcl is in opt/oommf (Windows).
    # This would probably also work on MacOS/Linux, but on these operating
    # systems, when installed via conda, we use 'oommf' executable.
    if sys.platform == 'win32' and \
       os.path.isdir(os.path.join(sys.prefix, 'conda-meta')):
        oommf_tcl = os.path.join(sys.prefix, 'opt', 'oommf', 'oommf.tcl')
        if os.path.isfile(oommf_tcl):
            _cached_oommf_runner = TclOOMMFRunner(oommf_tcl)
            return _cached_oommf_runner

    # OOMMF available as an executable - in a conda env on Mac/Linux, or oommf
    # installed separately.
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
                        f'stdout:\n{res.stdout}\n'
                        f'stderr:\n{res.stderr}')
        else:
            _cached_oommf_runner = DockerOOMMFRunner(docker_exe=docker_exe,
                                                     image='ubermag/oommf')
            return _cached_oommf_runner

    # If OOMMFRunner was not returned up to this point, we raise an
    # exception.
    raise EnvironmentError('Cannot find OOMMF.')


def status():
    """Run a macrospin example for 1 ps through oommfc and print the OOMMF
    status.

    Returns
    -------
    int

        If ``0``, the OOMMF is found and running. Otherwise, ``1`` is returned.

    Examples
    --------
    1. Checking the OOMMF status.

    >>> import oommfc as oc
    ...
    >>> oc.oommf.status()
    Running OOMMF...
    OOMMF found and running.
    0

    """
    system = mm.examples.macrospin()
    try:
        td = oc.TimeDriver()
        td.drive(system, t=1e-12, n=1)
        print('OOMMF found and running.')
        return 0
    except (EnvironmentError, RuntimeError):
        print('Cannot find OOMMF.')
        return 1


def overhead():
    """Run a macrospin example for 1 ps through ``oommfc`` and directly and
    return the difference in run times.

    Returns
    -------
    float

      The time difference (overhead) between running OOMMF though ``oommfc``
      and directly.

    Examples
    --------
    1. Getting the overhead time.

    >>> import oommfc as oc
    ...
    >>> isinstance(oc.oommf.overhead(), float)
    Running OOMMF...
    True

    """
    # Running OOMMF through oommfc.
    system = mm.examples.macrospin()
    td = oc.TimeDriver()
    oommfc_start = time.time()
    td.drive(system, t=1e-12, n=1, save=True, overwrite=True)
    oommfc_stop = time.time()
    oommfc_time = oommfc_stop - oommfc_start

    # Running OOMMF directly.
    oommf_runner = get_oommf_runner()
    mifpath = os.path.realpath(os.path.join(system.name,
                                            'drive-0',
                                            'macrospin.mif'))
    oommf_start = time.time()
    oommf_runner.call(mifpath)
    oommf_stop = time.time()
    oommf_time = oommf_stop - oommf_start
    oc.delete(system)

    return oommfc_time - oommf_time
