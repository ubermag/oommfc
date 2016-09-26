import os
from micromagneticmodel.drivers import Driver


class Driver(Driver):
    def drive(self):
        self.dirname = self.system.name + '/'
        if not os.path.exists(self.dirname):
            os.makedirs(self.dirname)
        self.mif_filename = self.dirname + self.system.name + '.mif'

        self.system.m.write_oommf_file(self.dirname+"m0file.omf")

        miffile = open(self.mif_filename, 'w')
        miffile.write(self.script())
        miffile.close()

        self.run_simulator()

    def run_simulator(self):
        if os.name == 'nt':
            oommf_command = 'tclsh86 %OOMMFTCL% boxsi +fg '
        else:
            oommf_command = 'tclsh $OOMMFTCL boxsi +fg '
        oommf_command += self.mif_filename
        oommf_command += ' -exitondone 1'
        os.system('cd ' + self.dirname)
        returncode = os.system(oommf_command)
        if returncode:
            raise Exception("Something has gone wrong in running OOMMF")
