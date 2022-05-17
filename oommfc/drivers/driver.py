import abc
import contextlib
import datetime
import glob
import json
import os

import discretisedfield as df
import micromagneticmodel as mm
import numpy as np
import ubermagtable as ut

import oommfc as oc


@contextlib.contextmanager
def _changedir(dirname):
    """Context manager for changing directory."""
    cwd = os.getcwd()
    os.chdir(dirname)
    try:
        yield
    finally:
        os.chdir(cwd)


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
        pass  # pragma: no cover

    def drive(
        self,
        system,
        /,
        dirname=".",
        append=True,
        fixed_subregions=None,
        compute=None,
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

        # system directory already exists
        if os.path.exists(os.path.join(dirname, system.name)):
            dirs = os.listdir(os.path.join(dirname, system.name))
            drive_dirs = [i for i in dirs if i.startswith("drive")]
            compute_dirs = [i for i in dirs if i.startswith("compute")]
            if compute is None:
                if drive_dirs:
                    if append:
                        numbers = list(zip(*[i.split("-") for i in drive_dirs]))[1]
                        numbers = list(map(int, numbers))
                        system.drive_number = max(numbers) + 1
                    else:
                        msg = (
                            f"Directory {system.name=} already exists. To "
                            "append drives to it, pass append=True."
                        )
                        raise FileExistsError(msg)
                else:
                    system.drive_number = 0
            else:
                if compute_dirs:
                    if append:
                        numbers = list(zip(*[i.split("-") for i in compute_dirs]))[1]
                        numbers = list(map(int, numbers))
                        system.compute_number = max(numbers) + 1
                    else:
                        msg = (
                            f"Directory {system.name=} already exists. To "
                            "append drives to it, pass append=True."
                        )
                        raise FileExistsError(msg)
                else:
                    system.compute_number = 0

        # Generate directory.
        if compute is None:
            subdir = f"drive-{system.drive_number}"
        else:
            subdir = f"compute-{system.compute_number}"

        workingdir = os.path.join(dirname, system.name, subdir)

        # Make a directory inside which OOMMF will be run.
        if not os.path.exists(workingdir):
            os.makedirs(workingdir)

        # compute tlist for time-dependent field (current)
        for term in system.energy:
            if hasattr(term, "func") and callable(term.func):
                self._time_dependence(term=term, **kwargs)

        # Change directory to workingdir
        with _changedir(workingdir):
            # Generate the necessary filenames.
            miffilename = f"{system.name}.mif"
            jsonfilename = "info.json"

            # Generate and save mif file.
            mif = oc.scripts.system_script(system, ovf_format=ovf_format)
            mif += oc.scripts.driver_script(
                self,
                system,
                fixed_subregions=fixed_subregions,
                output_step=output_step,
                compute=compute,
                **kwargs,
            )
            with open(miffilename, "w") as miffile:
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
                with open(jsonfilename, "w") as jsonfile:
                    jsonfile.write(json.dumps(info))

            if runner is None:
                runner = oc.runner.runner
            runner.call(
                argstr=miffilename,
                n_threads=n_threads,
                verbose=verbose,
                total=kwargs.get("n"),
                glob_name=system.name,
            )

            # Update system's m and datatable attributes if the derivation of
            # E, Heff, or energy density was not asked.
            if compute is None:
                # Update system's magnetisation. An example .omf filename:
                # test_sample-Oxs_TimeDriver-Magnetization-01-0000008.omf
                omffiles = glob.iglob(f"{system.name}*.omf")
                lastomffile = sorted(omffiles)[-1]
                # pass Field.array instead of Field for better performance
                system.m.value = df.Field.fromfile(lastomffile).array

                # Update system's datatable.
                if isinstance(self, oc.TimeDriver):
                    x = "t"
                elif isinstance(self, oc.MinDriver):
                    x = "iteration"
                elif isinstance(self, oc.HysteresisDriver):
                    x = "B_hysteresis"
                system.table = ut.Table.fromfile(f"{system.name}.odt", x=x)

        if compute is None:
            system.drive_number += 1
        else:
            system.compute_number += 1

        # remove information about fixed cells for subsequent runs
        if hasattr(self.evolver, "fixed_spins"):
            del self.evolver.fixed_spins

    def _time_dependence(self, term, **kwargs):
        try:
            tmax = kwargs["t"]
        except KeyError:
            msg = (
                f"Time-dependent term {term.__class__.__name__=} must be "
                "used with time driver."
            )
            raise RuntimeError(msg)
        ts = np.arange(0, tmax + term.dt, term.dt)
        try:  # vector output from term.func
            tlist = [list(term.func(t)) for t in ts]
            dtlist = (np.gradient(tlist)[0] / term.dt).tolist()
        except TypeError:  # scalar output from term.func
            tlist = [term.func(t) for t in ts]
            dtlist = list(np.gradient(tlist) / term.dt)
        term.tlist = tlist
        term.dtlist = dtlist
