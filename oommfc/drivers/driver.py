import abc
import os
import glob
import json
import shutil
import datetime
import oommfc as oc
import ubermagtable as ut
import discretisedfield as df
import micromagneticmodel as mm


class Driver(mm.Driver):
    def drive(self, system, overwrite=False, **kwargs):
        """Drives the system in phase space.

        Takes ``micromagneticmodel.System`` and drives it in the phase space.
        If ``overwrite=True`` is passed, the directory with all previously
        created files will be deleted before the system is run. This method
        accepts any other arguments that could be required by the specific
        driver. After the drive is executed, system's magnetisation and
        datatable will be updated.

        Parameters
        ----------
        system : micromagneticmodel.System

          System to be driven.

        overwrite : bool

          If ``True``, previously created files will be deleted. Defaults to
          ``False``.

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
        202...

        2. Drive system using time driver (``TimeDriver``).

        >>> system.energy.zeeman.H = (0, 1e6, 0)
        ...
        >>> td = oc.TimeDriver()
        >>> td.drive(system, t=0.1e-9, n=10)
        202...

        3. Delete files.

        >>> td.delete(system)

        """
        # This method is implemented in the derived class.
        self._checkargs(**kwargs)

        # Generate the necessary filenames.
        dirname = os.path.join(system.name, f'drive-{system.drive_number}')
        miffilename = f'{system.name}.mif'
        jsonfilename = 'info.json'

        # Check whether a directory with the same name as system.name already
        # exists. If it does, warn the user and tell him that he should pass
        # overwrite=True to the drive method.
        if os.path.exists(dirname):
            if overwrite:
                shutil.rmtree(system.name)
            else:
                msg = (f'Directory {system.name} already exists. To overwrite '
                       'it, pass overwrite=True to the drive method.')
                raise FileExistsError(msg)

        # Make a directory inside which OOMMF will be run.
        if not os.path.exists(dirname):
            os.makedirs(dirname)

        # Change directory to dirname
        cwd = os.getcwd()
        os.chdir(dirname)

        # Generate mif file.
        mif = '# MIF 2.2\n\n'
        # Output options
        mif += 'SetOptions {\n'
        mif += f'  basename {system.name}\n'
        mif += '  scalar_output_format %.12g\n'
        mif += '  scalar_field_output_format {text %#.15g}\n'
        mif += '  vector_field_output_format {text %#.15g}\n'
        mif += '}\n\n'
        # Mesh and energy scripts.
        mif += oc.script.mesh_script(system.m.mesh)
        mif += oc.script.energy_script(system.energy)

        # Driver script. kwargs are passed for TimeDriver.
        mif += self._script(system, **kwargs)

        # Save mif file.
        with open(miffilename, 'w') as miffile:
            miffile.write(mif)

        # Generate and save json info file.
        info = {}
        info['drive_number'] = system.drive_number
        info['date'] = datetime.datetime.now().strftime('%Y-%m-%d')
        info['time'] = datetime.datetime.now().strftime('%H:%M:%S')
        info['driver'] = self.__class__.__name__
        info['args'] = kwargs
        with open(jsonfilename, 'w') as jsonfile:
            jsonfile.write(json.dumps(info))

        # Run OOMMF.
        oommf = oc.oommf.get_oommf_runner()
        oommf.call(argstr=miffilename)

        # Update system's m and datatable attributes if the derivation of E,
        # Heff, or energy density was not asked.
        if 'derive' not in kwargs:
            # Update system's magnetisation. An example .omf filename:
            # test_sample-Oxs_TimeDriver-Magnetization-01-0000008.omf
            omffiles = glob.iglob(f'{system.name}*.omf')
            lastomffile = sorted(omffiles)[-1]
            system.m.value = df.Field.fromfile(lastomffile)

            # Update system's datatable.
            system.table = ut.read(f'{system.name}.odt')

        # Change directory back to cwd.
        os.chdir(cwd)

        # Increase the system's drive_number counter.
        system.drive_number += 1

    def delete(self, system):
        if os.path.exists(system.name):
            shutil.rmtree(system.name)

    @abc.abstractmethod
    def _checkargs(self, **kwargs):
        pass  # pragma: no cover
