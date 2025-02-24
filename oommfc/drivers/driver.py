import abc
import pathlib

import discretisedfield as df
import micromagneticmodel as mm
import numpy as np
import ubermagtable as ut
import ubermagutil as uu

import oommfc as oc


class Driver(mm.ExternalDriver):
    """Driver base class."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if hasattr(self, "evolver"):
            self.autoselect_evolver = False
        else:
            self.autoselect_evolver = True

    @abc.abstractmethod
    def _checkargs(self, kwargs):
        """Check drive keyword arguments.

        This method can also update keyword arguments where required. Changes must
        happen in-place, i.e. `kwargs` must be modified directly.
        """

    def drive_kwargs_setup(self, drive_kwargs):
        """Additional keyword arguments allowed for drive.

        This function tests additional keyword arguments that have been passed to the
        ``drive`` method (it is not intended for direct use). A drive in oommfc can
        accept the following additional keyword arguments.

        Parameters
        ----------
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

        """
        self._checkargs(drive_kwargs)
        drive_kwargs.setdefault("fixed_subregions", None)
        drive_kwargs.setdefault("output_step", False)
        drive_kwargs.setdefault("n_threads", None)
        drive_kwargs.setdefault("compute", None)

    def schedule_kwargs_setup(self, schedule_kwargs):
        """Additional keyword arguments allowed for schedule.

        This function tests additional keyword arguments that have been passed to the
        ``schedule`` method (it is not intended for direct use). A drive in oommfc can
        accept the following additional keyword arguments.

        It is the user's responsibility to ensure that OOMMF can be executed from the
        scheduled job. This would typically imply activating the conda environment in
        the schedule header.

        To control the number of threads that OOMMF uses export the environment variable
        ``OOMMF_THREADS`` in the header file. This variable should have the same value
        as the number of CPUs requested from the scheduling system. If not specified a
        default value that depends on the OOMMF installation (typically 4) is used.

        Note that OOMMF cannot run on multiple nodes.

        Parameters
        ----------
        fixed_subregions : list, optional

            List of strings, where each string is the name of the subregion in
            the mesh whose spins should remain fixed while the system is being
            driven. Defaults to ``None``.

        output_step : bool, optional

            If ``True``, output is saved at each step. Default to ``False``.

        compute : str, optional

            ``Schedule...`` MIF line which can be added to the OOMMF file to
            save additional data. Defaults to ``None``.

        """
        self._checkargs(schedule_kwargs)
        schedule_kwargs.setdefault("fixed_subregions", None)
        schedule_kwargs.setdefault("output_step", False)
        schedule_kwargs.setdefault("compute", None)

    def _write_input_files(self, system, **kwargs):
        self.write_mif(system, **kwargs)

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
        """Write the mif file and related files.

        Takes ``micromagneticmodel.System`` and write the mif file (and related files)
        to drive it in the phase space. The files are written directly to directory
        ``dirname`` (if not specified the current working directory). No additional
        subdirectiories are created. To save a specific value during an OOMMF run
        ``Schedule...`` line can be passed using ``compute``.

        This method accepts any other arguments that could be required by the
        specific driver.

        Users are generally not encouraged to use this method directly. Instead
        ``Driver.drive``, ``Driver.schedule``, or ``oommfc.schedule`` should be used to
        write the files an run the simulation. This method is provided to give advanced
        users full flexibility.

        Parameters
        ----------
        system : micromagneticmodel.System

            System object to be driven.

        dirname : str, optional

            Name of a directory in which the input files are stored.
            If not specified the current workinng
            directory is used.

        ovf_format : str

            Format of the magnetisation output files written by OOMMF. Can be
            one of ``'bin8'`` (binary, double precision), ``'bin4'`` (binary,
            single precision) or ``'txt'`` (text-based, double precision).
            Defaults to ``'bin8'``.

        fixed_subregions : list, optional

            List of strings, where each string is the name of the subregion in
            the mesh whose spins should remain fixed while the system is being
            driven. Defaults to ``None``.

        output_step : bool, optional

            If ``True``, output is saved at each step. Default to ``False``.

        compute : str, optional

            ``Schedule...`` MIF line which can be added to the OOMMF file to
            save additional data. Defaults to ``None``.

        .. seealso::

            :py:func:`~oommfc.Driver.drive`
            :py:func:`~oommfc.Driver.schedule`
            :py:func:`~oommfc.compute`

        """
        # compute tlist for time-dependent field/current
        for term in system.energy:
            if hasattr(term, "func") and callable(term.func):
                self._time_dependence(term=term, **kwargs)

        with uu.changedir(dirname):
            mif = oc.scripts.system_script(system, ovf_format=ovf_format)
            mif += oc.scripts.driver_script(
                self,
                system,
                fixed_subregions=fixed_subregions,
                output_step=output_step,
                compute=compute,
                **kwargs,
            )
            with open(self._miffilename(system), "w", encoding="utf-8") as miffile:
                miffile.write(mif)

        # remove information about fixed cells for subsequent runs
        if hasattr(self.evolver, "fixed_spins"):
            del self.evolver.fixed_spins

    def _call(self, system, runner, n_threads=None, verbose=1, **kwargs):
        if runner is None:
            runner = oc.runner.runner
        runner.call(
            argstr=self._miffilename(system),
            n_threads=n_threads,
            verbose=verbose,
            total=kwargs.get("n"),
            glob_name=f"{system.name}*.omf",
        )

    def _schedule_commands(self, system, runner):
        if runner is None:
            runner = oc.runner.runner
        return [
            f"export OOMMF_HOSTPORT=`{runner._launchhost(dry_run=True)}`",
            runner._call(argstr=self._miffilename(system), dry_run=True),
            runner._kill(dry_run=True),
        ]

    def _read_data(self, system):
        # Update system's magnetisation. An example .omf filename:
        # test_sample-Oxs_TimeDriver-Magnetization-01-0000008.omf
        omffiles = pathlib.Path(".").glob(f"{system.name}-*.omf")
        lastomffile = sorted(omffiles)[-1]
        # pass Field.array instead of Field to system.m.value
        # - to avoid overriding component labels
        # - to avoid overriding subregions
        # - for better performance
        system.m.array = df.Field.from_file(str(lastomffile)).array

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
        if isinstance(term.func(ts[0]), (list, tuple, np.ndarray)):
            tlist = [[float(x) for x in term.func(t)] for t in ts]
            dtlist = (np.gradient(tlist)[0] / term.dt).tolist()
        else:  # scalar output from term.func
            tlist = [float(term.func(t)) for t in ts]
            dtlist = list(np.gradient(tlist) / term.dt)
        term.tlist = tlist
        term.dtlist = dtlist

    @staticmethod
    def _miffilename(system):
        return f"{system.name}.mif"
