import os
import glob
import oommfodt
import micromagneticmodel as mm
import discretisedfield as df
import oommfc as oc


class Driver(mm.Driver):
    def drive(self, system, **kwargs):
        """
        Drive the system.

        """
        filenames = self._filenames(system)

        # Make a directory for saving OOMMF files.
        self._makedir(system)

        # Save system's magnetisation configuration omf file.
        omffilename = filenames["omffilename"]
        system.m.write_oommf_file(omffilename)

        miffilename = filenames["miffilename"]
        self._save_mif(system, **kwargs)

        self._run_simulator(system)
        self._update_system(system)

    def _makedir(self, system):
        """
        Create directory where OOMMF files are saved.
        """
        dirname = self._filenames(system)["dirname"]
        if not os.path.exists(dirname):
            os.makedirs(dirname)

    def _save_mif(self, system, **kwargs):
        """
        Save OOMMF configuration mif file.
        """
        mif = "# MIF 2.1\n\n"
        mif += system.script()
        mif += self.script(system, **kwargs)

        miffilename = self._filenames(system)["miffilename"]
        miffile = open(miffilename, "w")
        miffile.write(mif)
        miffile.close()

    def _run_simulator(self, system):
        dirname = self._filenames(system)["dirname"]
        miffilename = self._filenames(system)["miffilename"]

        oommf = oc.OOMMF()

        oommf.call_oommf(miffilename)

    def _update_system(self, system):
        self._update_m(system)
        self._update_dt(system)

    def _update_m(self, system):
        # Find last omf file.
        dirname = self._filenames(system)["dirname"]
        last_omf_file = max(glob.iglob("{}*.omf".format(dirname)),
                            key=os.path.getctime)

        # Update system's magnetisaton.
        m_field = df.read_oommf_file(last_omf_file)
        m_field.normalisedto = system.m.normalisedto
        m_field.normalise()
        system.m = m_field

    def _update_dt(self, system):
        # Find last odt file.
        dirname = self._filenames(system)["dirname"]
        last_odt_file = max(glob.iglob("{}*.odt".format(dirname)),
                            key=os.path.getctime)

        # Update system's datatable.
        system.dt = oommfodt.OOMMFodt(last_odt_file).df

    def _filenames(self, system):
        dirname = "{}/".format(system.name)
        omffilename = "{}m0.omf".format(dirname)
        miffilename = "{}{}.mif".format(dirname, system.name)

        filenames = {}
        filenames["dirname"] = dirname
        filenames["omffilename"] = omffilename
        filenames["miffilename"] = miffilename

        return filenames
