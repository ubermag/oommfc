import os
import functools
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


class OOMMFRunner(metaclass=abc.ABCMeta):
    """Abstract class for running OOMMF."""

    def call(self, argstr, need_stderr=False, n_threads=None):
        """Call OOMMF by passing ``argstr`` to OOMMF.

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
        res = self._call(argstr=argstr, need_stderr=need_stderr,
                         n_threads=n_threads)
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
                print(f'\tstdout: {stdout}')
                print(f'\tstderr: {stderr}')
                print('\n')
            raise RuntimeError('Error in OOMMF run.')

        return res

    @abc.abstractmethod
    def _call(self, argstr, need_stderr=False, n_threads=None):
        """This method should be implemented in subclass."""
        pass  # pragma: no cover

    @abc.abstractmethod
    def _kill(self, targets=('all',)):
        """This method should be implemented in subclass."""
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

    @functools.cached_property
    def version(self):
        """Return the OOMMF version.

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

    @functools.cached_property
    def platform(self):
        """Return platform seen by OOMMF.

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

    @property
    def status(self):
        """Run a macrospin example for 1 ps through oommfc and print the OOMMF
        status.

        Returns
        -------
        int
            If ``0``, the OOMMF is found and running. Otherwise, ``1`` is
            returned.

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

    @abc.abstractmethod
    def __repr__(self):
        pass  # pragma: no cover


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
        if sys.platform != 'win32':
            launchhost = sp.run(['tclsh', self.oommf_tcl, 'launchhost', '0'],
                                stdout=sp.PIPE)
            port = launchhost.stdout.decode('utf-8', 'replace').strip('\n')
            self.env = dict(OOMMF_HOSTPORT=port, **os.environ)

    def _call(self, argstr, need_stderr=False, n_threads=None):
        cmd = ['tclsh', self.oommf_tcl, 'boxsi', '+fg',
               argstr, '-exitondone', '1']

        # Not clear why we cannot get stderr and stdout on win32. Calls to
        # OOMMF get stuck.
        stdout = stderr = sp.PIPE
        if sys.platform == 'win32' and not need_stderr:
            stdout = stderr = None  # pragma: no cover

        if n_threads is not None:
            cmd += ['-threads', str(n_threads)]

        if sys.platform != 'win32':
            return sp.run(cmd, stdout=stdout, stderr=stderr, env=self.env)
        else:
            return sp.run(cmd, stdout=stdout, stderr=stderr)

    def _kill(self, targets=('all',)):
        if sys.platform != 'win32':
            sp.run(['tclsh', self.oommf_tcl, 'killoommf'] + list(targets),
                   env=self.env)
        else:
            sp.run(['tclsh', self.oommf_tcl, 'killoommf'] + list(targets))

    def errors(self):
        errors_file = os.path.join(os.path.dirname(self.oommf_tcl),
                                   'boxsi.errors')
        with open(errors_file, 'r') as f:
            errors = f.read()

        return errors

    def __repr__(self):
        return f'TclOOMMFRunner({self.oommf_tcl})'


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
        launchhost = sp.run([self.oommf_exe, 'launchhost', '0'],
                            stdout=sp.PIPE)
        port = launchhost.stdout.decode('utf-8', 'replace').strip('\n')
        self.env = dict(OOMMF_HOSTPORT=port, **os.environ)

    def _call(self, argstr, need_stderr=False, n_threads=None):
        # Here we might need stderr = stdot = None like in
        # TclOOMMFRunner for Windows.  This is not clear because we
        # never use ExeOOMMFRunner on Windows.
        cmd = [self.oommf_exe, 'boxsi', '+fg', argstr, '-exitondone', '1']
        if n_threads is not None:
            cmd += ['-threads', str(n_threads)]
        return sp.run(cmd, stdout=sp.PIPE, stderr=sp.PIPE, env=self.env)

    def _kill(self, targets=('all',)):
        sp.run([self.oommf_exe, 'killoommf'] + list(targets), env=self.env)

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

    def __repr__(self):
        return f'ExeOOMMFRunner({self.oommf_exe})'


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

    def _call(self, argstr, need_stderr=False, n_threads=None):
        cmd = [self.docker_exe, 'run', '-v', os.getcwd()+':/io',
               self.image, '/bin/bash', '-c',
               ('tclsh /usr/local/oommf/oommf/oommf.tcl boxsi '
                '+fg {} -exitondone 1').format(argstr)]
        if n_threads is not None:
            cmd += ['-threads', str(n_threads)]
        return sp.run(cmd, stdout=sp.PIPE, stderr=sp.PIPE)

    def _kill(self, targets=('all',)):
        # There is no need to kill OOMMF when run inside docker.
        pass

    def errors(self):
        msg = 'boxsi.errors cannot be retrieved from Docker container.'
        raise EnvironmentError(msg)


class Runner:
    """Control the default runner.

    Parameters
    ----------
    cache_runner : bool
        If ``True`` the best way to run OOMMF is only determined once and the
        result is cached. Subsequent calls to the property ``runner`` will
        return the ``OOMMFRunner`` object from the cache. Setting this
        parameter to ``False`` will cause it to check for available methods
        again. Defaults to ``True``.

    envvar : str
        Name of the environment variable containing the path to ``oommf.tcl``.
        Defaults to ``'OOMMFTCL'``.

    oommf_exe : str
        The name or path of the executable ``oommf`` command. Defaults to
        ``'oommf'``.

    docker_exe : str
        The name or path of the docker command. Defaults to ``'docker'``.
    """

    def __init__(self):
        self.cache_runner = True
        self.envvar = 'OOMMFTCL'
        self.oommf_exe = 'oommf'
        self.docker_exe = 'docker'
        self._runner = None

    @property
    def runner(self):
        """Return default OOMMF runner.

        This property also allows to set a specific ``OOMMFRunner``. Before
        setting, a new runner is first checked to be functional by calling
        ``runner.status``.

        Examples
        --------
        1. Getting OOMMF Runner.

        >>> import oommfc as oc
        ...
        >>> runner = oc.runner.runner
        >>> isinstance(runner, oc.oommf.OOMMFRunner)
        True
        """
        if self.cache_runner and self._runner is not None:
            log.debug('Returning ceched runner.')
            return self._runner
        self.autoselect_runner()
        return self._runner

    @runner.setter
    def runner(self, runner):
        if runner.status == 1:
            raise ValueError(f'{runner=} cannot be used.')
        self._runner = runner

    def autoselect_runner(self):
        """Find the best available way to run OOMMF.

        The function tries to find a suitable runner by checking ``envvar``,
        ``ooommf_exe``, and ``docker_runner`` in the given order. If no runner
        can be found an ``EnvironmentError`` is raised.

        This method is also used to determine the default runner for the
        ``runner`` property as long as no runner has been cached. The method
        can be used to reset the default runner when a different runner has
        been set explicitly.

        Raises
        ------
        EnvironmentError
            If no OOMMF can be found on host.

        Examples
        --------
        1. Setting best runner

        >>> import oommfc as oc
        ...
        >>> oc.runner.autoselect_runner()
        >>> isinstance(oc.runner.runner, oc.oommf.OOMMFRunner)
        True
        """
        log.debug(f"Starting get_oommf_runner(use_cache={self.cache_runner}, "
                  f"envvar={self.envvar}, oommf_exe={self.oommf_exe}, "
                  f"docker_exe={self.docker_exe})")

        # Check for the OOMMFTCL environment variable pointing to oommf.tcl.
        log.debug(f"Step 1: Checking for the '{self.envvar=}' environment "
                  "variable pointing to oommf.tcl.")
        oommf_tcl = os.environ.get(self.envvar, None)
        if oommf_tcl is not None:
            cmd = [
                'tclsh', oommf_tcl, 'boxsi', '+fg', '+version', '-exitondone',
                '1'
            ]
            try:
                res = sp.run(cmd, stdout=sp.PIPE, stderr=sp.PIPE)
            except FileNotFoundError:
                log.warning('oommf.tcl was not found.')
            else:
                if res.returncode:
                    log.warning(
                        'OOMMFTCL is set, but OOMMF could not be run.\n'
                        f'stdout:\n{res.stdout}\nstderr:\n{res.stderr}')
                else:
                    self._runner = TclOOMMFRunner(oommf_tcl)
                    return

        # OOMMF is installed via conda and oommf.tcl is in opt/oommf (Windows).
        # This would probably also work on MacOS/Linux, but on these operating
        # systems, when installed via conda, we use 'oommf' executable.
        log.debug(
            "Step 2: are we on Windows and oommf is installed via conda?")
        if sys.platform == 'win32' and \
           os.path.isdir(os.path.join(sys.prefix, 'conda-meta')):
            oommf_tcl = os.path.join(sys.prefix, 'opt', 'oommf', 'oommf.tcl')
            if os.path.isfile(oommf_tcl):
                self._runner = TclOOMMFRunner(oommf_tcl)
                return

        # OOMMF available as an executable - in a conda env on Mac/Linux, or
        # oommf installed separately.
        log.debug(f"Step 3: is '{self.oommf_exe=}' in PATH? "
                  "Could be from conda env or manual install")
        oommf_exe = shutil.which(self.oommf_exe)
        log.debug(f"Ouput from 'which oommf_exe' = {oommf_exe}")
        if oommf_exe:
            cmd = [oommf_exe, 'boxsi',
                   '+fg', '+version', '-exitondone', '1']

            log.debug("Attempt command call")  # DEBUG
            res = sp.run(cmd, stdout=sp.PIPE, stderr=sp.PIPE)
            log.debug(res)

            if res.returncode == 0:
                self._runner = ExeOOMMFRunner(oommf_exe)
                return
            else:
                log.warning(f'{oommf_exe=} found but not executable.')
                log.debug(f"exitcode = {res.returncode}")
                if res.returncode == 127:  # maybe oommf is a pyenv shim?
                    pass

        # Check for docker to run OOMMF in a docker image.
        log.debug("Step 4: Can we use docker to host OOMMF?"
                  f" ('{self.docker_exe}')")
        cmd = [self.docker_exe, 'images']
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
                self._runner = DockerOOMMFRunner(docker_exe=self.docker_exe,
                                                 image='ubermag/oommf')
                return

        # If OOMMFRunner was not returned up to this point, we raise an
        # exception.
        raise EnvironmentError('Cannot find OOMMF.')

    def __repr__(self):
        # avoid selecting a runner when calling __repr__
        _runner = self._runner if self._runner is not None else "UNSET"

        return (f'OOMMF runner: {_runner}\n'
                f'runner is cached: {self.cache_runner}')


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
    oommf_runner = oc.runner.runner
    mifpath = os.path.realpath(os.path.join(system.name,
                                            'drive-0',
                                            'macrospin.mif'))
    oommf_start = time.time()
    oommf_runner.call(mifpath)
    oommf_stop = time.time()
    oommf_time = oommf_stop - oommf_start
    oc.delete(system)

    return oommfc_time - oommf_time
