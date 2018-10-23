import os
import glob
import json
import oommfodt
import micromagneticmodel as mm
import discretisedfield as df
import oommfc as oc
from datetime import datetime


class Driver(mm.Driver):
    def drive(self, system, **kwargs):
        """
        Drive the system.

        """
        self._check_args(**kwargs)

        filenames = self._filenames(system)

        # Make a directory for saving OOMMF files.
        self._makedir(system)

        # Save system's magnetisation configuration omf file.
        omffilename = filenames["omffilename"]
        system.m.write(omffilename)

        miffilename = filenames["miffilename"]
        self._save_mif(system, **kwargs)

        self._run_simulator(system)

        if "derive" not in kwargs:
            self._update_system(system)

        # info to json file
        self._write_info(system)

        # Increase counter
        system.drive_number += 1

    def _makedir(self, system):
        """
        Create directory where OOMMF files are saved.
        """
        dirname = self._filenames(system)["dirname"]
        if not os.path.exists(dirname):
            os.makedirs(dirname)

        subdirname = self._filenames(system)['subdirname']
        if not os.path.exists(subdirname):
            os.makedirs(subdirname)

    def _save_mif(self, system, **kwargs):
        """
        Save OOMMF configuration mif file.
        """
        mif = "# MIF 2.1\n\n"
        mif += system._script
        mif += self._script(system, **kwargs)

        miffilename = self._filenames(system)["miffilename"]
        miffile = open(miffilename, "w")
        miffile.write(mif)
        miffile.close()

    def _run_simulator(self, system):
        miffilename = self._filenames(system)["miffilename"]
        oommf = oc.oommf.get_oommf_runner()
        oommf.call(argstr=miffilename)

    def _update_system(self, system):
        self._update_m(system)
        self._update_dt(system)

    def _update_m(self, system):
        # Find last omf file.
        subdirname = self._filenames(system)["subdirname"]
        last_omf_file = max(glob.iglob("{}/*.omf".format(subdirname)),
                            key=os.path.getctime)

        # Update system's magnetisaton.
        m_field = df.read(last_omf_file)

        # Temporary solution for having script in mesh object.
        # Overwrites the df.Mesh with oc.Mesh.
        m_field.mesh = system.m.mesh

        system.m = m_field

    def _update_dt(self, system):
        # Find last odt file.
        subdirname = self._filenames(system)["subdirname"]
        last_odt_file = max(glob.iglob("{}/*.odt".format(subdirname)),
                            key=os.path.getctime)

        # Update system's datatable.
        system.dt = oommfodt.read(last_odt_file)

    def _filenames(self, system):
        dirname = os.path.join(system.name, "")
        subdirname = os.path.join(dirname, 'drive-{}'.format(system.drive_number))
        omffilename = os.path.join(subdirname, "m0.omf")
        miffilename = os.path.join(subdirname, "{}.mif".format(system.name))

        filenames = {}
        filenames["dirname"] = dirname
        filenames["subdirname"] = subdirname
        filenames["omffilename"] = omffilename
        filenames["miffilename"] = miffilename

        return filenames

    def _write_info(self, system):
        dirname = self._filenames(system)["subdirname"]
        filename = "{}/info.json".format(dirname)

        info = {}
        info['date'] = datetime.now().strftime('%Y-%m-%d')
        info['time'] = datetime.now().strftime('%H:%M')

        with open(filename, "w") as f:
            f.write(json.dumps(info))

