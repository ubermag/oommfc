import os
from micromagneticmodel.drivers import MinDriver


class MinDriver(MinDriver):
    def script(self):
        mif = "# MIF 2.1\n\n"
        mif += self.system.mesh.script()
        mif += self.system.hamiltonian.script()
        mif += "Specify Oxs_CGEvolve {}\n\n"
        mif += "# MinDriver\n"
        mif += "Specify Oxs_MinDriver {\n"
        mif += "  evolver Oxs_CGEvolve\n"
        mif += "  stopping_mxHxm 0.01\n"
        mif += "  mesh :{}\n".format(self.system.mesh.name)
        mif += "  Ms {}\n".format(self.system.m.normalisedto)
        mif += "  m0 {\n"
        mif += "    Oxs_FileVectorField {\n"
        mif += "      atlas :atlas\n"
        mif += "      norm 1.0\n"
        mif += "      file m0file.omf\n"
        mif += "    }\n"
        mif += "  }\n"
        mif += "  basename {}\n".format(self.system.name)
        mif += "  vector_field_output_format {text %\#.8g}\n"
        mif += "}\n\n"
        mif += "Destination table mmArchive\n"
        mif += "Destination mags mmArchive\n\n"
        mif += "Schedule DataTable table Stage 1\n"
        mif += "Schedule Oxs_MinDriver::Spin mags Stage 1"

        return mif

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

