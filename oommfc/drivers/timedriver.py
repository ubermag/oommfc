from .driver import Driver


class TimeDriver(Driver):
    def _script(self, system, **kwargs):
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

        meshname = system.m.mesh.name
        systemname = system.name
        if "derive" in kwargs:
            t, n = 1e-20, 1
        else:
            t, n = kwargs["t"], kwargs["n"]

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

        mif += "# m0 file\n"
        mif += "Specify Oxs_FileVectorField:m0file {\n"
        mif += "   atlas :atlas\n"
        mif += "   file m0.omf\n"
        mif += "}\n\n"

        mif += "# TimeDriver\n"
        mif += "Specify Oxs_TimeDriver {\n"
        mif += "  evolver {}\n".format(evolver)
        mif += "  stopping_time {}\n".format(t/n)
        mif += "  mesh :{}\n".format(meshname)
        mif += "  stage_count {}\n".format(n)
        if "total_iteration_limit" in kwargs:
            mif += "  total_iteration_limit {}\n".format(total_iteration_limit)
        elif "derive" in kwargs:
            mif += "  total_iteration_limit {}\n".format(1)

        mif += "  Ms {\n"
        mif += "    Oxs_VecMagScalarField {\n"
        mif += "      field :m0file\n"
        mif += "    }\n"
        mif += "  }\n"
        mif += "  m0 :m0file\n"
        mif += "  basename {}\n".format(systemname)
        mif += "  scalar_field_output_format {text %\#.15g}\n"
        mif += "  vector_field_output_format {text %\#.15g}\n"
        mif += "}\n\n"
        mif += "Destination table mmArchive\n"
        mif += "Destination mags mmArchive\n"
        mif += "Destination archive mmArchive\n\n"
        if "derive" in kwargs:
            if "ield" in kwargs["derive"] or "density" in kwargs["derive"]:
                mif += ("Schedule \"{}\" archive "
                        "Step 1".format(kwargs["derive"]))
            else:
                mif += "Schedule DataTable table Stage 1\n"
        else:
            mif += "Schedule DataTable table Stage 1\n"
            mif += "Schedule Oxs_TimeDriver::Magnetization mags Stage 1"

        return mif

    def _check_args(self, **kwargs):
        if "derive" in kwargs:
            pass
        else:
            if kwargs["t"] <= 0:
                raise ValueError("Expected t > 0.")
            if kwargs["n"] <= 0 or not isinstance(kwargs["n"], int):
                raise ValueError("Expected n > 0.")
