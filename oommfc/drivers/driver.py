import os
import sys
import abc
import glob
import json
import shutil
import datetime
import contextlib
import oommfc as oc
import ubermagtable as ut
import discretisedfield as df
import micromagneticmodel as mm


@contextlib.contextmanager
def _changedir(dirname):
    """Context manager for changing directory.

    """
    cwd = os.getcwd()
    os.chdir(dirname)
    try:
        yield
    finally:
        os.chdir(cwd)


class Driver(mm.Driver):
    @abc.abstractmethod
    def _checkargs(self, **kwargs):
        """Abstract method defined in a derived driver class.

        """
        pass  # pragma: no cover

    def drive(self, system, append=True, compute=None, runner=None, **kwargs):
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

        append : bool

            If ``True`` and the system directory already exists, drive or
            compute directories will be appended.

        compute : str

            ``Schedule...`` MIF line which can be added to the OOMMF file to
            save additional data. Defaults to ``None``.

        runner : oommfc.oommf.OOMMFRunner

            OOMMF Runner which is going to be used for running OOMMF. If
            ``None``, OOMMF runner will be found automatically. Defaults to
            ``None``.

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

        if os.path.exists(system.name):  # system directory already exists
            dirs = os.listdir(system.name)
            drive_dirs = [i for i in dirs if i.startswith('drive')]
            compute_dirs = [i for i in dirs if i.startswith('compute')]
            if compute is None:
                if drive_dirs:
                    if append:
                        numbers = list(zip(*[i.split('-')
                                             for i in drive_dirs]))[1]
                        numbers = list(map(int, numbers))
                        system.drive_number = max(numbers) + 1
                    else:
                        msg = (f'Directory {system.name} already exists. To '
                               f'append drives to it, pass append=True to the '
                               f'drive method.')
                        raise FileExistsError(msg)
                else:
                    system.drive_number = 0
            else:
                if compute_dirs:
                    if append:
                        numbers = list(zip(*[i.split('-')
                                             for i in compute_dirs]))[1]
                        numbers = list(map(int, numbers))
                        system.drive_number = max(numbers) + 1
                    else:
                        msg = (f'Directory {system.name} already exists. To '
                               f'append drives to it, pass append=True to the '
                               f'drive method.')
                        raise FileExistsError(msg)
                else:
                    system.compute_number = 0

        # Generate directory.
        if compute is None:
            subdir = f'drive-{system.drive_number}'
        else:
            subdir = f'compute-{system.compute_number}'

        dirname = os.path.join(system.name, subdir)

        # Make a directory inside which OOMMF will be run.
        if not os.path.exists(dirname):
            os.makedirs(dirname)

        # Change directory to dirname
        with _changedir(dirname):
            # Generate the necessary filenames.
            miffilename = f'{system.name}.mif'
            jsonfilename = 'info.json'

            # Generate and save mif file.
            mif = oc.scripts.system_script(system)
            mif += oc.scripts.driver_script(self, system, compute=compute,
                                            **kwargs)
            with open(miffilename, 'w') as miffile:
                miffile.write(mif)

            # Generate and save json info file for a drive (not compute).
            if compute is None:
                info = {}
                info['drive_number'] = system.drive_number
                info['date'] = datetime.datetime.now().strftime('%Y-%m-%d')
                info['time'] = datetime.datetime.now().strftime('%H:%M:%S')
                info['driver'] = self.__class__.__name__
                info['args'] = kwargs
                with open(jsonfilename, 'w') as jsonfile:
                    jsonfile.write(json.dumps(info))

            # Get right OOMMF runner depending on whether there is DMI.
            if runner is None:
                if sys.platform != 'win32':
                    runner = oc.oommf.get_oommf_runner()
                else:
                    if hasattr(system.energy, 'dmi'):
                        if (system.energy.dmi.crystalclass == 'Cnv' and
                                system.m.mesh.bc == ''):
                            runner = oc.oommf.get_oommf_runner()
                        else:
                            runner = oc.oommf.DockerOOMMFRunner()
                    else:
                        runner = oc.oommf.get_oommf_runner()

            runner.call(argstr=miffilename)

            # Update system's m and datatable attributes if the derivation of
            # E, Heff, or energy density was not asked.
            if compute is None:
                # Update system's magnetisation. An example .omf filename:
                # test_sample-Oxs_TimeDriver-Magnetization-01-0000008.omf
                omffiles = glob.iglob(f'{system.name}*.omf')
                lastomffile = sorted(omffiles)[-1]
                system.m.value = df.Field.fromfile(lastomffile)

                # Update system's datatable.
                system.table = ut.Table.fromfile(f'{system.name}.odt')

        if compute is None:
            system.drive_number += 1
        else:
            system.compute_number += 1
