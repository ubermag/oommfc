from .driver import Driver


class TimeDriver(Driver):
    def script(self, system, **kwargs):
        alpha = system.dynamics.damping.alpha
        gamma = system.dynamics.precession.gamma
        meshname = system.mesh.name
        Ms = system.m.normalisedto
        systemname = system.name

        mif = "# RungeKuttaEvolver\n"
        mif += "Specify Oxs_RungeKuttaEvolve:evolver {\n"
        mif += "  alpha {}\n".format(alpha)
        mif += "  gamma_G {}\n".format(gamma)
        mif += "}\n\n"
        mif += "# TimeDriver\n"
        mif += "Specify Oxs_TimeDriver {\n"
        mif += "  evolver Oxs_RungeKuttaEvolve\n"
        mif += "  stopping_time {}\n".format(kwargs["t"]/kwargs["n"])
        mif += "  mesh :{}\n".format(meshname)
        mif += "  stage_count {}\n".format(kwargs["n"])
        mif += "  Ms {}\n".format(Ms)
        mif += "  m0 {\n"
        mif += "    Oxs_FileVectorField {\n"
        mif += "      atlas :atlas\n"
        mif += "      norm 1.0\n"
        mif += "      file m0.omf\n"
        mif += "    }\n"
        mif += "  }\n"
        mif += "  basename {}\n".format(systemname)
        mif += "  vector_field_output_format {text %\#.8g}\n"
        mif += "}\n\n"
        mif += "Destination table mmArchive\n"
        mif += "Destination mags mmArchive\n\n"
        mif += "Schedule DataTable table Stage 1\n"
        mif += "Schedule Oxs_TimeDriver::Spin mags Stage 1"

        return mif
