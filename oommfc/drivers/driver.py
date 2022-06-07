import abc
import datetime
import json
import pathlib
import subprocess as sp
import sys

import discretisedfield as df
import micromagneticmodel as mm
import numpy as np
import ubermagtable as ut

import oommfc as oc
import oommfc.util


class Driver(mm.Driver):
    """Driver base class."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if hasattr(self, "evolver"):
            self.autoselect_evolver = False
        else:
            self.autoselect_evolver = True

    @abc.abstractmethod
    def _checkargs(self, **kwargs):
        """Abstract method for checking arguments."""

    @property
    @abc.abstractmethod
    def _x(self):
        """Independent variable."""

    def drive(
        self,
        system,
        /,
        dirname=".",
        append=True,
        fixed_subregions=None,
        output_step=False,
        n_threads=None,
        runner=None,
        ovf_format="bin8",
        verbose=1,
        **kwargs,
    ):
        """Drives the system in phase space.

        Takes ``micromagneticmodel.System`` and drives it in the phase space.
        If ``append=True`` and the system director already exists, drive will
        be appended to that directory. Otherwise, an exception will be raised.
        To save a specific value during an OOMMF run ``Schedule...`` line can
        be passed using ``compute``. To specify the way OOMMF is run, an
        ``oommfc.oommf.OOMMFRunner`` can be passed using ``runner``.

        This method accepts any other arguments that could be required by the
        specific driver.

        Parameters
        ----------
        system : micromagneticmodel.System

            System object to be driven.

        append : bool, optional

            If ``True`` and the system directory already exists, drive or
            compute directories will be appended. Defaults to ``True``.

        fixed_subregions : list, optional

            List of strings, where each string is the name of the subregion in
            the mesh whose spins should remain fixed while the system is being
            driven. Defaults to ``None``.

        output_step : bool, optional

            If ``True``, output is saved at each step. Default to ``False``.

        n_threads : int, optional

            Controls the number of threads that OOMMF uses. The number can alternatively
            also be controlled via the environment variable ``OOMMF_THREADS``. If not
            specified a default value that depends on the OOMMF installation (typically
            4) is used.

        compute : str, optional

            ``Schedule...`` MIF line which can be added to the OOMMF file to
            save additional data. Defaults to ``None``.

        runner : oommfc.oommf.OOMMFRunner, optional

            OOMMF Runner which is going to be used for running OOMMF. If
            ``None``, OOMMF runner will be found automatically. Defaults to
            ``None``.

        ovf_format : str

            Format of the magnetisation output files written by OOMMF. Can be
            one of ``'bin8'`` (binary, double precision), ``'bin4'`` (binary,
            single precision) or ``'txt'`` (text-based, double precision).
            Defaults to ``'bin8'``.

        verbose : int, optional

            If ``verbose=0``, no output is printed. For ``verbose=1`` information about
            the OOMMF runner and the runtime is printed to stdout. For ``verbose=2`` a
            progress bar is displayed for TimeDriver drives. Note that this information
            only relies on the number of magnetisation snapshots already saved to disk
            and therefore only gives a rough indication of progress. Defaults to ``1``.

        Raises
        ------
        FileExistsError

            If system directory already exists and append=False.

        Examples
        --------
        1. Drive system using minimisation driver (``MinDriver``).

        >>> import micromagneticmodel as mm
        >>> import discretisedfield as df
        >>> import oommfc as oc
        ...
        >>> system = mm.System(name='my_cool_system')
        >>> system.energy = mm.Exchange(A=1e-12) + mm.Zeeman(H=(0, 0, 1e6))
        >>> mesh = df.Mesh(p1=(0, 0, 0), p2=(1e-9, 1e-9, 10e-9), n=(1, 1, 10))
        >>> system.m = df.Field(mesh, dim=3, value=(1, 1, 1), norm=1e6)
        ...
        >>> md = oc.MinDriver()
        >>> md.drive(system)
        Running OOMMF...

        2. Drive system using time driver (``TimeDriver``).

        >>> system.energy.zeeman.H = (0, 1e6, 0)
        ...
        >>> td = oc.TimeDriver()
        >>> td.drive(system, t=0.1e-9, n=10)
        Running OOMMF...

        """
        # This method is implemented in the derived driver class. It raises
        # exception if any of the arguments are not valid.
        self._checkargs(**kwargs)

        workingdir = self._setup_working_directory(
            system=system, dirname=dirname, mode="drive", append=append
        )

        with oc.util.changedir(workingdir):
            self.write_mif(
                system=system,
                ovf_format=ovf_format,
                fixed_subregions=fixed_subregions,
                output_step=output_step,
                compute=None,
                **kwargs,
            )
            self._call(
                system=system,
                runner=runner,
                n_threads=n_threads,
                verbose=verbose,
                total=kwargs.get("n"),
            )
            self._read_data(system)

        system.drive_number += 1

    def schedule(
        self,
        system,
        schedule_cmd,
        schedule_header,
        /,
        schedule_file_name="job.sh",
        dirname=".",
        append=True,
        fixed_subregions=None,
        output_step=False,
        n_threads=None,
        runner=None,
        ovf_format="bin8",
        verbose=1,
        **kwargs,
    ):
        """Schedule drive of the system in phase space.

        Takes ``micromagneticmodel.System`` and drives it in the phase space. This
        method writes the input files for OOMMF and then submits a job to the machines
        job scheduling system, e.g. Slurm. The command to schedule and the required
        resources in a format understood by the schedule command must be passed to the
        function.

        If ``append=True`` and the system director already exists, drive will
        be appended to that directory. Otherwise, an exception will be raised.
        To save a specific value during an OOMMF run ``Schedule...`` line can
        be passed using ``compute``. To specify the way OOMMF is run, an
        ``oommfc.oommf.OOMMFRunner`` can be passed using ``runner``.

        This method accepts any other arguments that could be required by the
        specific driver.

        Parameters
        ----------
        system : micromagneticmodel.System

            System object to be driven.

        schedule_cmd : str

            Name of the scheduling system submission program, e.g. ``'sbatch'`` for
            slurm.

        schedule_header : str

            Filename of the submission header file or str with the data to specify
            system requirements such as number of CPUs and memory. Note that OOMMF
            cannot run on multiple nodes.

        schedule_file_name : str, optional

            Name of the newly created OOMMF run script that is scheduled for execution.

        append : bool, optional

            If ``True`` and the system directory already exists, drive or
            compute directories will be appended. Defaults to ``True``.

        fixed_subregions : list, optional

            List of strings, where each string is the name of the subregion in
            the mesh whose spins should remain fixed while the system is being
            driven. Defaults to ``None``.

        output_step : bool, optional

            If ``True``, output is saved at each step. Default to ``False``.

        n_threads : int, optional

            Controls the number of threads that OOMMF uses. The number can alternatively
            also be controlled via the environment variable ``OOMMF_THREADS``. If not
            specified a default value that depends on the OOMMF installation (typically
            4) is used.

        compute : str, optional

            ``Schedule...`` MIF line which can be added to the OOMMF file to
            save additional data. Defaults to ``None``.

        runner : oommfc.oommf.OOMMFRunner, optional

            OOMMF Runner which is going to be used for running OOMMF. If
            ``None``, OOMMF runner will be found automatically. Defaults to
            ``None``.

        ovf_format : str

            Format of the magnetisation output files written by OOMMF. Can be
            one of ``'bin8'`` (binary, double precision), ``'bin4'`` (binary,
            single precision) or ``'txt'`` (text-based, double precision).
            Defaults to ``'bin8'``.

        verbose : int, optional

            If ``verbose=0``, no output is printed. For ``verbose=1`` information about
            the OOMMF runner and the runtime is printed to stdout. For ``verbose=2`` a
            progress bar is displayed for TimeDriver drives. Note that this information
            only relies on the number of magnetisation snapshots already saved to disk
            and therefore only gives a rough indication of progress. Defaults to ``1``.

        Raises
        ------
        FileExistsError

            If system directory already exists and append=False.

        Examples
        --------
        1. Drive system using minimisation driver (``MinDriver``).

        >>> import micromagneticmodel as mm
        >>> import discretisedfield as df
        >>> import oommfc as oc
        ...
        >>> system = mm.System(name='my_cool_system')
        >>> system.energy = mm.Exchange(A=1e-12) + mm.Zeeman(H=(0, 0, 1e6))
        >>> mesh = df.Mesh(p1=(0, 0, 0), p2=(1e-9, 1e-9, 10e-9), n=(1, 1, 10))
        >>> system.m = df.Field(mesh, dim=3, value=(1, 1, 1), norm=1e6)
        ...
        >>> md = oc.MinDriver()
        >>> md.drive(system)
        Running OOMMF...

        2. Drive system using time driver (``TimeDriver``).

        >>> system.energy.zeeman.H = (0, 1e6, 0)
        ...
        >>> td = oc.TimeDriver()
        >>> td.drive(system, t=0.1e-9, n=10)
        Running OOMMF...

        """
        # This method is implemented in the derived driver class. It raises
        # exception if any of the arguments are not valid.
        self._checkargs(**kwargs)

        workingdir = self._setup_working_directory(
            system=system, dirname=dirname, mode="drive", append=append
        )

        if pathlib.Path(schedule_header).exists():
            with open(schedule_header, "rt") as f:
                header = f.read()
        else:
            header = schedule_header

        with oc.util.changedir(workingdir):
            self.write_mif(
                system=system,
                ovf_format=ovf_format,
                fixed_subregions=fixed_subregions,
                output_step=output_step,
                compute=None,
                **kwargs,
            )

            if runner is None:
                runner = oc.runner.runner
            run_cmd = runner._call(
                argstr=self._miffilename(system), n_threads=n_threads, dry_run=True
            )
            with open(schedule_file_name, "wt") as f:
                f.write(header)
                f.write("\n")
                f.write(" ".join(run_cmd))

            stdout = stderr = sp.PIPE
            if sys.platform == "win32":
                stdout = stderr = None  # pragma: no cover

            if verbose >= 1:
                print(
                    f"Running '{schedule_cmd} {schedule_file_name}' in"
                    f" '{workingdir.absolute()}'."
                )
            system.drive_number += 1
            res = sp.run(
                [schedule_cmd, schedule_file_name], stdout=stdout, stderr=stderr
            )

            # remove information about fixed cells for subsequent runs
            if hasattr(self.evolver, "fixed_spins"):
                del self.evolver.fixed_spins

            if res.returncode != 0:
                msg = "Error during job schedule.\n"
                msg += f"command: {schedule_cmd} {schedule_file_name}\n"
                if sys.platform != "win32":
                    # Only on Linux and MacOS - on Windows we do not get stderr and
                    # stdout.
                    stderr = res.stderr.decode("utf-8", "replace")
                    stdout = res.stdout.decode("utf-8", "replace")
                    msg += f"stdout: {stdout}\n"
                    msg += f"stderr: {stderr}\n"
                raise RuntimeError(msg)

    @staticmethod
    def _setup_working_directory(system, dirname, mode, append=True):
        system_dir = pathlib.Path(dirname, system.name)
        try:
            last_existing_simulation = max(
                system_dir.glob(f"{mode}*"), key=lambda p: int(p.name.split("-")[1])
            )
            next_number = int(last_existing_simulation.name.split("-")[1]) + 1
        except ValueError:  # glob did not find any directories
            next_number = 0
        if next_number > 0 and not append:
            raise FileExistsError(
                f"Directory {system.name=} already exists. To "
                "append drives to it, pass append=True."
            )
        setattr(system, f"{mode}_number", next_number)
        workingdir = system_dir / f"{mode}-{next_number}"
        workingdir.mkdir(parents=True)
        return workingdir

    def write_mif(
        self,
        system,
        dirname=".",
        ovf_format="bin8",
        fixed_subregions=None,
        output_step=False,
        compute=None,
        **kwargs,
    ):
        """Write the mif file and related files."""
        # compute tlist for time-dependent field/current
        for term in system.energy:
            if hasattr(term, "func") and callable(term.func):
                self._time_dependence(term=term, **kwargs)

        with oc.util.changedir(dirname):
            mif = oc.scripts.system_script(system, ovf_format=ovf_format)
            mif += oc.scripts.driver_script(
                self,
                system,
                fixed_subregions=fixed_subregions,
                output_step=output_step,
                compute=compute,
                **kwargs,
            )
            with open(self._miffilename(system), "wt") as miffile:
                miffile.write(mif)

            # Generate and save json info file for a drive (not compute).
            if compute is None:
                info = {}
                info["drive_number"] = system.drive_number
                info["date"] = datetime.datetime.now().strftime("%Y-%m-%d")
                info["time"] = datetime.datetime.now().strftime("%H:%M:%S")
                info["driver"] = self.__class__.__name__
                for k, v in kwargs.items():
                    info[k] = v
                with open("info.json", "wt") as jsonfile:
                    jsonfile.write(json.dumps(info))

    def _call(self, system, runner, n_threads, verbose, total=None):
        if runner is None:
            runner = oc.runner.runner
        try:
            runner.call(
                argstr=self._miffilename(system),
                n_threads=n_threads,
                verbose=verbose,
                total=total,
                glob_name=system.name,
            )
        finally:
            # remove information about fixed cells for subsequent runs
            if hasattr(self.evolver, "fixed_spins"):
                del self.evolver.fixed_spins

    def _read_data(self, system):
        # Update system's magnetisation. An example .omf filename:
        # test_sample-Oxs_TimeDriver-Magnetization-01-0000008.omf
        omffiles = pathlib.Path(".").glob(f"{system.name}*.omf")
        lastomffile = sorted(omffiles)[-1]
        # pass Field.array instead of Field for better performance
        # and to avoid overriding custom component labels
        system.m.value = df.Field.fromfile(str(lastomffile)).array
        # Update system's datatable.
        system.table = ut.Table.fromfile(f"{system.name}.odt", x=self._x)

    @staticmethod
    def _time_dependence(term, **kwargs):
        try:
            tmax = kwargs["t"]
        except KeyError:
            raise RuntimeError(
                f"Time-dependent term {term.__class__.__name__=} must be "
                "used with time driver."
            ) from None
        ts = np.arange(0, tmax + term.dt, term.dt)
        try:  # vector output from term.func
            tlist = [list(term.func(t)) for t in ts]
            dtlist = (np.gradient(tlist)[0] / term.dt).tolist()
        except TypeError:  # scalar output from term.func
            tlist = [term.func(t) for t in ts]
            dtlist = list(np.gradient(tlist) / term.dt)
        term.tlist = tlist
        term.dtlist = dtlist

    @staticmethod
    def _miffilename(system):
        return f"{system.name}.mif"
