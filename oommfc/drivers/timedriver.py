from .driver import Driver


class TimeDriver(Driver):
    def script(self, system, **kwargs):
        try:
            alpha = system.dynamics.damping.alpha
        except AttributeError:
            alpha = 0
        try:
            gamma = system.dynamics.precession.gamma
        except AttributeError:
            gamma = 2.211e5
        try:
            u = system.dynamics.stt.u
            beta = system.dynamics.stt.beta
        except AttributeError:
            stt = False
        else:
            stt = True

        meshname = system.mesh.name
        Ms = system.m.normalisedto
        systemname = system.name

        if not stt:
            mif = "# RungeKuttaEvolver\n"
            mif += "Specify Oxs_RungeKuttaEvolve:evolver {\n"
            mif += "  alpha {}\n".format(alpha)
            mif += "  gamma_G {}\n".format(gamma)
            mif += "}\n\n"
            evolver = "Oxs_RungeKuttaEvolve"
        else:
            mif = "# SpinTransferTorqueEvolver\n"
            mif += "Specify Anv_SpinTEvolve {\n"
            mif += "  do_precess 1\n"
            mif += "  gamma_G {}\n".format(gamma)
            mif += "  alpha {}\n".format(alpha)
            mif += "  method rkf54s\n"
            mif += "  u {\n"
            mif += "    Oxs_UniformScalarField {\n"
            mif += "      value {}\n".format(u[0])
            mif += "    }\n"
            mif += "  }\n"
            mif += "  beta {}\n".format(beta)
            mif += "}\n\n"
            evolver = "Anv_SpinTEvolve"

        mif += "# TimeDriver\n"
        mif += "Specify Oxs_TimeDriver {\n"
        mif += "  evolver {}\n".format(evolver)
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
