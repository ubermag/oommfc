import os
from micromagneticmodel.drivers import Driver


class Driver(Driver):
    def drive(self, system):
        """
        Drive the system using energy minimisation driver.

        """
        # Make directory for saving OOMMF files.
        dirname = "{}/".format(system.name)
        self._makedirs(dirname)

        # Save system's magnetisation configuration omf file.
        omffilename = "{}m0file.omf".format(dirname)
        system.m.write_oommf_file(omffilename)

        miffilename = "{}{}.mif".format(dirname, system.name)
        self.save_mif(system, miffilename)

        # Run simulation.
        self.run_simulator(dirname, miffilename)

        # Update system.
        self.update_system()

    def _makedirs(self, dirname):
        """
        Create directory where OOMMF files are saved.
        """
        if not os.path.exists(dirname):
            os.makedirs(dirname)

    def save_mif(self, system, miffilename):
        """
        Save OOMMF configuration mif file.
        """
        mif = "# MIF 2.1\n\n"
        mif += system.script()
        mif += self.script(system)
        
        miffile = open(miffilename, 'w')
        miffile.write(mif)
        miffile.close()

    def run_simulator(self, dirname, miffilename):
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

    def update_system(self):
        pass
