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
        """Drives the system object.

        This method takes a `oommfc.System` object and drives in the
        phase space. If `overwrite=True` is passed then the directory
        with all previously created files will be deleted before the
        run is executed. This method accepts any other arguments that
        could be required by the specific driver. After the drive is
        executed, the magnetisation and datatable of the system's
        object will be updated.

        Parameters
        ----------
        system : oommfc.System
          System object to be driven
        overwrite : bool
          If True, then the previously created files will be deleted.

        """
        # This method is implemented in the derived class.
        self._checkargs(**kwargs)

        # Generate the necessary filenames.
        dirname = os.path.join(system.name, f'drive-{system.drive_number}')
        miffilename = f'{system.name}.mif'
        jsonfilename = 'info.json'

        # Check whether a directory with the same name as system.name
        # already exists. If it does, warn the user and tell him that
        # he should pass overwrite=True to the drive method.
        if os.path.exists(dirname):
            if overwrite:
                shutil.rmtree(system.name)
            else:
                msg = (f'Directory with name={dirname} already exists. '
                       'If you want to overwrite it, pass overwrite=True '
                       'to the drive method. Otherwise, change the name '
                       'of the system or delete the directory by running '
                       'system.delete().')
                raise FileExistsError(msg)

        # Make a directory inside which OOMMF will be run.
        if not os.path.exists(dirname):
            os.makedirs(dirname)

        # Change directory to dirname
        cwd = os.getcwd()
        os.chdir(dirname)

        # Generate and save mif file.
        mif = '# MIF 2.2\n\n'
        # Output options
        mif += 'SetOptions {\n'
        mif += f'  basename {system.name}\n'
        mif += '  scalar_output_format %.12g\n'
        mif += '  scalar_field_output_format {text %#.15g}\n'
        mif += '  vector_field_output_format {text %#.15g}\n'
        mif += '}\n\n'
        mif += system._script
        mif += self._script(system, **kwargs)
        with open(miffilename, 'w') as miffile:
            miffile.write(mif)

        # Create json info file.
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

        # Update system's m and dt attributes if the derivation of E,
        # Heff, or energy density was not asked.
        if 'derive' not in kwargs:
            # Update system's magnetisation. An example .omf filename:
            # test_sample-Oxs_TimeDriver-Magnetization-01-0000008.omf
            omffiles = glob.iglob(f'{system.name}*.omf')
            lastomffile = sorted(omffiles)[-1]
            m_field = df.Field.fromfile(lastomffile)

            # This line exists because the mesh generated in
            # df.Field.fromfile method comes from the discretisedfield
            # module where the _script method is not implemented.
            m_field.mesh = system.m.mesh
            system.m = m_field

            # Update system's datatable.
            system.dt = ut.read(f'{system.name}.odt')

        # Change directory back to cwd.
        os.chdir(cwd)

        # Increase the system's drive_number counter.
        system.drive_number += 1

    def _checkargs(self, **kwargs):
        raise NotImplementedError
