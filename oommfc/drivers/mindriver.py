import os
from .driver import Driver


class MinDriver(Driver):
    def script(self, system):
        mif = "# CGEvolver\n"
        mif += "Specify Oxs_CGEvolve {}\n\n"
        mif += "# MinDriver\n"
        mif += "Specify Oxs_MinDriver {\n"
        mif += "  evolver Oxs_CGEvolve\n"
        mif += "  stopping_mxHxm 0.01\n"
        mif += "  mesh :{}\n".format(system.mesh.name)
        mif += "  Ms {}\n".format(system.m.normalisedto)
        mif += "  m0 {\n"
        mif += "    Oxs_FileVectorField {\n"
        mif += "      atlas :atlas\n"
        mif += "      norm 1.0\n"
        mif += "      file m0file.omf\n"
        mif += "    }\n"
        mif += "  }\n"
        mif += "  basename {}\n".format(system.name)
        mif += "  vector_field_output_format {text %\#.8g}\n"
        mif += "}\n\n"
        mif += "Destination table mmArchive\n"
        mif += "Destination mags mmArchive\n\n"
        mif += "Schedule DataTable table Stage 1\n"
        mif += "Schedule Oxs_MinDriver::Spin mags Stage 1"
        return mif
