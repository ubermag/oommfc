import os
import glob
from micromagneticmodel.drivers import Driver
from discretisedfield import read_oommf_file
from oommfodt import OOMMFodt


class Driver(Driver):
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
        miffile = open(miffilename, 'w')
        miffile.write(mif)
        miffile.close()

    def _run_simulator(self, system):
        dirname = self._filenames(system)["dirname"]
        miffilename = self._filenames(system)["miffilename"]

        if os.name == 'nt':
            oommf_command = 'tclsh86 %OOMMFTCL% boxsi +fg '
        else:
            oommf_command = 'tclsh $OOMMFTCL boxsi +fg '
        oommf_command += miffilename
        oommf_command += ' -exitondone 1'
        os.system('cd ' + dirname)
        returncode = os.system(oommf_command)
        if returncode:
            raise Exception("Something has gone wrong in running OOMMF")

    def _update_system(self, system):
        self._update_m(system)
        self._update_dt(system)

    def _update_m(self, system):
        # Find last omf file.
        dirname = self._filenames(system)["dirname"]
        last_omf_file = max(glob.iglob("{}*.omf".format(dirname)),
                            key=os.path.getctime)

        # Update system's magnetisaton.
        system.m = read_oommf_file(last_omf_file,
                                   normalisedto=system.m.normalisedto)

    def _update_dt(self, system):
        # Find last odt file.
        dirname = self._filenames(system)["dirname"]
        last_odt_file = max(glob.iglob("{}*.odt".format(dirname)),
                            key=os.path.getctime)

        # Update system's datatable.
        system.dt = OOMMFodt(last_odt_file).df

    def _filenames(self, system):
        dirname = "{}/".format(system.name)
        oommffilename = "{}m0file.omf".format(dirname)
        miffilename = "{}{}.mif".format(dirname, system.name)

        filenames = {}
        filenames["dirname"] = dirname
        filenames["oommffilename"] = oommffilename
        filenames["miffilename"] = miffilename

        return filenames
