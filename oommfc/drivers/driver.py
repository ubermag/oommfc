import os
import glob
import json
import oommfc as oc
import oommfodt as oo
import discretisedfield as df
import micromagneticmodel as mm
import datetime


class Driver(mm.Driver):
    def drive(self, system, **kwargs):
        # This method is implemented in the derived class (TimeDriver,
        # MinDriver,...).
        self._check_args(**kwargs)

        # Generate the necessary filenames.
        self.dirname = os.path.join(system.name, 'drive-{}'.format(system.drive_number))
        self.omffilename = os.path.join(self.dirname, "m0.omf")
        self.miffilename = os.path.join(self.dirname, "{}.mif".format(system.name))

        # Make a directory inside which OOMMF will be run.
        self._makedir()

        # Generate and save mif file.
        self._makemif(system, **kwargs)

        # Save system's initial magnetisation omf file.
        self._makeomf()

        self._run_simulator(system)

        if "derive" not in kwargs:
            self._update_system(system)

        # info to json file
        self._write_info(system)

        # Increase counter
        system.drive_number += 1

    def _makedir(self):
        if not os.path.exists(self.dirname):
            os.makedirs(self.dirname)

    def _makemif(self, system, **kwargs):
        mif = "# MIF 2.1\n\n"
        mif += system._script
        mif += self._script(system, **kwargs)

        miffile = open(self.miffilename, "w")
        miffile.write(mif)
        miffile.close()

    def _makeomf(self):
        system.m.write(self.omffilename)

    def _run_simulator(self, system):
        oommf = oc.oommf.get_oommf_runner()
        oommf.call(argstr=self.miffilename)

    def _update_system(self, system):
        self._update_m(system)
        self._update_dt(system)

    def _update_m(self, system):
        # Find last omf file.
        last_omf_file = max(glob.iglob("{}/*.omf".format(self.dirname)),
                            key=os.path.getctime)

        # Update system's magnetisaton.
        m_field = df.read(last_omf_file)

        # Temporary solution for having script in mesh object.
        # Overwrites the df.Mesh with oc.Mesh.
        m_field.mesh = system.m.mesh

        system.m = m_field

    def _update_dt(self, system):
        # Find last odt file.
        last_odt_file = max(glob.iglob("{}/*.odt".format(self.dirname)),
                            key=os.path.getctime)

        # Update system's datatable.
        system.dt = oo.read(last_odt_file)

    def _write_info(self, system):
        filename = "{}/info.json".format(self.dirname)

        info = {}
        info['date'] = datetime.datetime.now().strftime('%Y-%m-%d')
        info['time'] = datetime.datetime.now().strftime('%H:%M:%S')

        with open(filename, "w") as f:
            f.write(json.dumps(info))

