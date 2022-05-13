import abc
import datetime
import logging
import os
import shutil
import subprocess as sp
import sys
import time

import micromagneticmodel as mm
import ubermagutil as uu

import oommfc as oc

from .progressbar import ProgressBar

log = logging.getLogger("oommfc")


class OOMMFRunner(metaclass=abc.ABCMeta):
    """Abstract class for running OOMMF."""

    def __del__(self):
        """Kill all OOMMF applications when object goes out of scope.

        On Windows we must kill OOMMF after each call because file ownerships
        are otherwise not correct. As a consequence ``oommfc.delete`` does not
        work without killing.

        """
        if sys.platform != "win32":
            self._kill()

    def call(
        self,
        argstr,
        need_stderr=False,
        n_threads=None,
        verbose=1,
        total=None,
        glob_name="",
    ):
        """Call OOMMF by passing ``argstr`` to OOMMF.

        Parameters
        ----------
        argstr : str

            Argument string passed to OOMMF.

        need_stderr : bool, optional

            If ``need_stderr=True``, standard error is captured. Defaults to
            ``False``.

        verbose : int, optional

            If ``verbose=0``, no output is printed. For ``verbose=1`` information about
            the OOMMF runner and the runtime is printed to stdout. For ``verbose=2`` a
            progress bar is displayed for TimeDriver drives. Note that this information
            only relies on the number of magnetisation snapshots already saved to disk
            and therefore only gives a rough indication of progress. Defaults to ``1``.

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
        >>> runner = oc.runner.runner
        >>> runner.call(argstr='+version')
        Running OOMMF...
        CompletedProcess(...)

        """
        if verbose >= 1:
            now = datetime.datetime.now()
            timestamp = "{}/{:02d}/{:02d} {:02d}:{:02d}".format(
                now.year, now.month, now.day, now.hour, now.minute
            )
            if verbose >= 2 and total:
                progress_bar_thread = ProgressBar(
                    total, self.__class__.__name__, glob_name
                )
                progress_bar_thread.start()
            else:
                print(
                    f"Running OOMMF ({self.__class__.__name__})[{timestamp}]... ",
                    end="",
                )
                tic = time.time()

        res = self._call(argstr=argstr, need_stderr=need_stderr, n_threads=n_threads)
        if sys.platform == "win32":
            self._kill()  # required for oc.delete; oommf keeps file ownership

        if verbose >= 1:
            if verbose >= 2 and total:
                progress_bar_thread.terminate()
            else:
                toc = time.time()
                seconds = "({:0.1f} s)".format(toc - tic)
                print(seconds)  # append seconds to the previous print.

        if res.returncode != 0:
            msg = "Error in OOMMF run.\n"
            cmdstr = " ".join(res.args)
            msg += f"command: {cmdstr}\n"
            if sys.platform != "win32":
                # Only on Linux and MacOS - on Windows we do not get stderr and
                # stdout.
                stderr = res.stderr.decode("utf-8", "replace")
                stdout = res.stdout.decode("utf-8", "replace")
                msg += f"stdout: {stdout}\n"
                msg += f"stderr: {stderr}\n"
            raise RuntimeError(msg)

        return res

    @abc.abstractmethod
    def _call(self, argstr, need_stderr=False, n_threads=None):
        """This method should be implemented in subclass."""
        pass  # pragma: no cover

    @abc.abstractmethod
    def _kill(self, targets=("all",)):
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

    @property
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
        >>> runner = oc.runner.runner
        >>> runner.version
        '...'

        """
        res = self.call(argstr="+version", need_stderr=True, verbose=0)
        return res.stderr.decode("utf-8").split("OOMMF")[-1].strip()

    @property
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
        >>> runner = oc.runner.runner
        >>> runner.platform
        '...'

        """
        # in 2.0a3 platform information is written to stdout
        res = self.call(argstr="+platform", need_stderr=True, verbose=0)
        return res.stdout.decode("utf-8")

    @property
    def status(self):
        """Run a macrospin example for 1 ps through oommfc and print the OOMMF
        status.

        Returns
        -------
        int
            If ``0``, then OOMMF is found and running. Otherwise, ``1`` is
            returned.

        Examples
        --------
        1. Checking the OOMMF status.

        >>> import oommfc as oc
        ...
        >>> oc.runner.runner.status
        Running OOMMF...
        OOMMF found and running.
        0

        """
        system = mm.examples.macrospin()
        try:
            td = oc.TimeDriver()
            td.drive(system, t=1e-12, n=1, runner=self)
            print("OOMMF found and running.")
            return 0
        except (EnvironmentError, RuntimeError):
            print("Cannot find OOMMF.")
            return 1

    @abc.abstractmethod
    def __repr__(self):
        pass  # pragma: no cover


@uu.inherit_docs
class NativeOOMMFRunner(OOMMFRunner):
    """OOMMF runner using oommf installed on the system.

    Base class for ``TclOOMMFRunner`` and ``ExeOOMMFRunner``.
    Derived classes must implement a ``List`` ``self.oommf``.

    """

    def __init__(self):
        # oommf launchhost gets stuck on Windows
        # -> it is not possible to run multiple calculations in parallel
        if sys.platform != "win32":
            launchhost = sp.run([*self.oommf, "launchhost", "0"], stdout=sp.PIPE)
            port = launchhost.stdout.decode("utf-8", "replace").strip("\n")
            self.env = dict(OOMMF_HOSTPORT=port, **os.environ)
        else:
            self.env = os.environ

    def _call(self, argstr, need_stderr=False, n_threads=None):
        cmd = [*self.oommf, "boxsi", "+fg", argstr, "-exitondone", "1"]

        # Not clear why we cannot get stderr and stdout on win32. Calls to
        # OOMMF get stuck.
        stdout = stderr = sp.PIPE
        if sys.platform == "win32" and not need_stderr:
            stdout = stderr = None  # pragma: no cover

        if n_threads is not None:
            cmd += ["-threads", str(n_threads)]

        return sp.run(cmd, stdout=stdout, stderr=stderr, env=self.env)

    def _kill(self, targets=("all",)):
        sp.run([*self.oommf, "killoommf", "-q"] + list(targets), env=self.env)


@uu.inherit_docs
class TclOOMMFRunner(NativeOOMMFRunner):
    """OOMMF runner using path to ``oommf.tcl``.

    Parameters
    ----------
    oommf_tcl: str

        Path to ``oommf.tcl`` file.

    """

    def __init__(self, oommf_tcl):
        self.oommf_tcl = oommf_tcl  # a path to oommf.tcl
        self.oommf = ["tclsh", self.oommf_tcl]
        super().__init__()

    def errors(self):
        errors_file = os.path.join(os.path.dirname(self.oommf_tcl), "boxsi.errors")
        with open(errors_file, "r") as f:
            errors = f.read()

        return errors

    def __repr__(self):
        return f"TclOOMMFRunner({self.oommf_tcl})"


@uu.inherit_docs
class ExeOOMMFRunner(NativeOOMMFRunner):
    """OOMMF runner using OOMMF executable, which can be found on $PATH.

    Parameters
    ----------
    oommf_exe: str

        Name of the OOMMF executable. Defaults to ``oommf``.

    """

    def __init__(self, oommf_exe="oommf"):
        self.oommf_exe = shutil.which(oommf_exe)
        self.oommf = [self.oommf_exe]
        super().__init__()

    def errors(self):
        try:
            errors_file = os.path.join(
                os.path.dirname(shutil.which(self.oommf_exe)),
                "..",
                "opt",
                "oommf",
                "boxsi.errors",
            )
            with open(errors_file, "r") as f:
                errors = f.read()
            return errors

        except FileNotFoundError:
            msg = "boxsi.errors cannot be retrieved."
            raise EnvironmentError(msg)

    def __repr__(self):
        return f"ExeOOMMFRunner({self.oommf_exe})"


@uu.inherit_docs
class DockerOOMMFRunner(OOMMFRunner):
    """OOMMF runner using Docker.

    Parameters
    ----------
    docker_exe: str

        Docker executable. Defaults to ``docker``.

    image: str

        Docker image on DockerHub. Defaults to ``oommf/oommf:20a3``.

    selinux : bool, optional

        If ``True`` use additional ``:z`` flag for the mounted directories. This can be
        required to get read/write access when using SELinux. Use with caution and check
        the Docker documentation on SELinux:
        https://docs.docker.com/storage/bind-mounts/#configure-the-selinux-label.
        Alternatively, you can set SELinux to Permissive Mode to get read/write access.
        Defaults to ``False``.

    """

    def __init__(self, docker_exe="docker", image="oommf/oommf:20a3", selinux=False):
        self.docker_exe = docker_exe
        self.image = image
        self.selinux = selinux

    def _call(self, argstr, need_stderr=False, n_threads=None):
        cmd = [
            self.docker_exe,
            "run",
            "-v",
            f"{os.getcwd()}:/io{':z' if self.selinux else ''}",
            self.image,
            "/bin/bash",
            "-c",
            (
                "tclsh /usr/local/oommf/oommf/oommf.tcl boxsi +fg {} -exitondone 1"
            ).format(argstr),
        ]
        if n_threads is not None:
            cmd += ["-threads", str(n_threads)]
        return sp.run(cmd, stdout=sp.PIPE, stderr=sp.PIPE)

    def _kill(self, targets=("all",)):
        # There is no need to kill OOMMF when run inside docker.
        pass

    def errors(self):
        msg = "boxsi.errors cannot be retrieved from Docker container."
        raise EnvironmentError(msg)

    def __repr__(self):
        return f"DockerOOMMFRunner(docker_exe={self.docker_exe}, image={self.image})"


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
        self.envvar = "OOMMFTCL"
        self.oommf_exe = "oommf"
        self.docker_exe = "docker"
        self._runner = None

    @property
    def runner(self):
        """Return default OOMMF runner.

        The default runner is determined using ``autoselect_runner()``. If
        ``cache_runner`` is ``True`` the runner is cached during the first call
        and the same runner is returned in subsequent calls to this property.

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

        2. Setting OOMMF Runner.

        >>> import oommfc as oc  # doctest: +SKIP
        ...
        >>> oc.runner.runner = oc.oommf.DockerOOMMFRunner()  # doctest: +SKIP
        Running OOMMF ...
        OOMMF found and running.
        >>> isinstance(oc.runner.runner,
        ...            oc.oommf.DockerOOMMFRunner)  # doctest: +SKIP
        True

        """
        if self.cache_runner and self._runner is not None:
            log.debug("Returning cached runner.")
            return self._runner
        self.autoselect_runner()
        return self._runner

    @runner.setter
    def runner(self, runner):
        if runner.status != 0:
            raise ValueError(f"{runner=} cannot be used.")
        self._runner = runner

    def autoselect_runner(self):
        """Find the best available way to run OOMMF.

        The function tries to find a suitable runner by checking ``envvar``,
        ``ooommf_exe``, and ``docker_runner``, in this order. If no runner
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
        log.debug(
            "Starting autoselect_runner: cache_runner=%(cache_runner)s, "
            "envvar=%(envvar)s, oommf_exe=%(oommf_exe)s, "
            "docker_exe=%(docker_exe)s)",
            {
                "cache_runner": self.cache_runner,
                "envvar": self.envvar,
                "oommf_exe": self.oommf_exe,
                "docker_exe": self.docker_exe,
            },
        )

        # Check for the OOMMFTCL environment variable pointing to oommf.tcl.
        log.debug(
            "Step 1: Checking for the self.envvar=%(envvar)s environment"
            " variable pointing to oommf.tcl.",
            {"envvar": self.envvar},
        )
        oommf_tcl = os.environ.get(self.envvar, None)
        if oommf_tcl is not None:
            cmd = ["tclsh", oommf_tcl, "boxsi", "+fg", "+version", "-exitondone", "1"]
            try:
                res = sp.run(cmd, stdout=sp.PIPE, stderr=sp.PIPE)
            except FileNotFoundError:
                log.warning("oommf.tcl was not found.")
            else:
                if res.returncode:
                    log.warning(
                        "OOMMFTCL is set, but OOMMF could not be run.\n"
                        "stdout:\n%(stdout)s\nstderr:\n%(stderr)s",
                        {"stdout": res.stdout, "stderr": res.stderr},
                    )
                else:
                    self._runner = TclOOMMFRunner(oommf_tcl)
                    return

        # OOMMF available as an executable - in a conda env on Mac/Linux, or
        # oommf installed separately.
        log.debug(
            "Step 2: is oommf_exe=%(oommf_exe)s in PATH? "
            "Could be from conda env or manual install.",
            {"oommf_exe": self.oommf_exe},
        )
        oommf_exe = shutil.which(self.oommf_exe)
        log.debug(
            'Ouput from "which oommf_exe"=%(oommf_exe)s', {"oommf_exe": oommf_exe}
        )
        if oommf_exe:
            cmd = [
                oommf_exe,
                "boxsi",
                "+fg",
                "+version",
                "-exitondone",
                "1",
                "-kill",
                "all",
            ]

            stdout = stderr = sp.PIPE
            if sys.platform == "win32":
                stdout = stderr = None  # pragma: no cover

            log.debug("Attempt command call")  # DEBUG
            res = sp.run(cmd, stdout=stdout, stderr=stderr)
            log.debug(res)

            if res.returncode == 0:
                self._runner = ExeOOMMFRunner(oommf_exe)
                return
            else:
                log.warning(
                    "oommf_exe=%(exe)s found but not executable.", {"exe": oommf_exe}
                )
                log.debug("exitcode = %(returncode)s", {"returncode": res.returncode})
                if res.returncode == 127:  # maybe oommf is a pyenv shim?
                    pass

        # Check for docker to run OOMMF in a docker image.
        log.debug(
            'Step 3: Can we use docker to host OOMMF? ("docker_exe=%(docker_exe)s")',
            {"docker_exe": self.docker_exe},
        )
        cmd = [self.docker_exe, "images"]
        try:
            res = sp.run(cmd, stdout=sp.PIPE, stderr=sp.PIPE)
        except FileNotFoundError:
            log.warning("Docker was not found.")
        else:
            if res.returncode != 0:
                log.warning(
                    "Error running docker\nstdout:\n%(stdout)s\nstderr:\n%(stderr)s",
                    {"stdout": res.stdout, "stderr": res.stderr},
                )
            else:
                self._runner = DockerOOMMFRunner(docker_exe=self.docker_exe)
                return

        # If OOMMFRunner was not returned up to this point, we raise an
        # exception.
        raise EnvironmentError("Cannot find OOMMF.")

    def __repr__(self):
        # avoid selecting a runner when calling __repr__
        _runner = self._runner if self._runner is not None else "UNSET"

        return f"OOMMF runner: {_runner}\nrunner is cached: {self.cache_runner}"


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
    mifpath = os.path.realpath(os.path.join(system.name, "drive-0", "macrospin.mif"))
    oommf_start = time.time()
    oommf_runner.call(mifpath)
    oommf_stop = time.time()
    oommf_time = oommf_stop - oommf_start
    oc.delete(system)

    return oommfc_time - oommf_time
