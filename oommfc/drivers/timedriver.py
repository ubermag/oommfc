import os
from .driver import Driver


class TimeDriver(Driver):
    def script(self, system, **kwargs):
        mif = "# RungeKuttaEvolver\n"
        mif += "Specify Oxs_RungeKuttaEvolve:evolver {\n"
        mif += "  alpha {}\n".format(system.dynamics.damping.alpha)
        mif += "  gamma_G {}\n".format(system.dynamics.precession.gamma)
        mif += "}\n\n"
        mif += "# TimeDriver\n"
        mif += "Specify Oxs_TimeDriver {\n"
        mif += "  evolver Oxs_RungeKuttaEvolve\n"
        mif += "  stopping_time {}\n".format(kwargs["t"]/kwargs["n"])
        mif += "  mesh :{}\n".format(system.mesh.name)
        mif += "  stage_count {}\n".format(kwargs["n"])
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
        mif += "Schedule Oxs_TimeDriver::Spin mags Stage 1"
        return mif
