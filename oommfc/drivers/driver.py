import os
import glob
import json
import shutil
import datetime
import oommfc as oc
import oommfodt as oo
import discretisedfield as df
import micromagneticmodel as mm


class Driver(mm.Driver):
    def drive(self, system, overwrite=False, **kwargs):
        # This method is implemented in the derived class (TimeDriver,
        # MinDriver,...).
        self._check_args(**kwargs)

        # Generate the necessary filenames.
        self.dirname = os.path.join(system.name,
                                    'drive-{}'.format(system.drive_number))
        self.omffilename = os.path.join(self.dirname, 'm0.omf')
        self.miffilename = os.path.join(self.dirname,
                                        '{}.mif'.format(system.name))
        self.jsonfilename = os.path.join(self.dirname, 'info.json')

        # Check whether a directory with the same name as system.name
        # already exists. If it does, warn the user and tell him that
        # he should pass overwrite=True to the drive method.
        self._checkdir(system, overwrite=overwrite)

        # Make a directory inside which OOMMF will be run.
        self._makedir()

        # Generate and save mif file.
        self._makemif(system, **kwargs)

        # Save system's initial magnetisation omf file.
        self._makeomf(system)

        # Create json info file.
        self._makejson()

        # Run OOMMF.
        self._run_oommf()

        # Update system's m and dt attributes if the derivation of E,
        # Heff, or energy density was not asked.
        if 'derive' not in kwargs:
            self._update_m(system)
            self._update_dt(system)

        # Increase the system's drive_number counter.
        system.drive_number += 1

    def _checkdir(self, system, overwrite=False):
        if os.path.exists(self.dirname):
            if not overwrite:
                msg = ('Directory with name={} already exists. If you want '
                       'to overwrite it, pass overwrite=True to the drive '
                       'method. Otherwise, change the name of the system '
                       'or delete the directory by running '
                       'system.delete().'.format(self.dirname))
                raise FileExistsError(msg)
            else:
                shutil.rmtree(system.name)

    def _makedir(self):
        if not os.path.exists(self.dirname):
            os.makedirs(self.dirname)

    def _makemif(self, system, **kwargs):
        mif = '# MIF 2.1\n\n'
        mif += system._script
        mif += self._script(system, **kwargs)

        with open(self.miffilename, 'w') as miffile:
            miffile.write(mif)

    def _makeomf(self, system):
        system.m.write(self.omffilename)

    def _makejson(self):
        info = {}
        info['date'] = datetime.datetime.now().strftime('%Y-%m-%d')
        info['time'] = datetime.datetime.now().strftime('%H:%M:%S')

        with open(self.jsonfilename, 'w') as jsonfile:
            jsonfile.write(json.dumps(info))

    def _run_oommf(self):
        oommf = oc.oommf.get_oommf_runner()
        oommf.call(argstr=self.miffilename)

    def _update_m(self, system):
        last_omf_file = max(glob.iglob(os.path.join(self.dirname, '*.omf')),
                            key=os.path.getctime)
        m_field = df.read(last_omf_file)

        # This line exists because the mesh generated in df.read
        # method comes from the discrtisedfield module where the
        # _script method is not implemented.
        m_field.mesh = system.m.mesh

        system.m = m_field

    def _update_dt(self, system):
        last_odt_file = max(glob.iglob(os.path.join(self.dirname, '*.odt')),
                            key=os.path.getctime)
        system.dt = oo.read(last_odt_file)
