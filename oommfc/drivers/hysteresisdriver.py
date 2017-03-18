from .driver import Driver


class HysteresisDriver(Driver):
    def _script(self, system, **kwargs):
        meshname = system.m.mesh.name
        systemname = system.name
        Hmin = kwargs["Hmin"]
        Hmax = kwargs["Hmax"]
        n = kwargs["n"]

        mif = "# m0 file\n"
        mif += "Specify Oxs_FileVectorField:m0file {\n"
        mif += "   atlas :atlas\n"
        mif += "   file m0.omf\n"
        mif += "}\n\n"

        mif += "# UZeeman\n"
        mif += "Specify Oxs_UZeeman {\n"
        mif += "  Hrange {\n"
        mif += "    {{ {} {} {} {} {} {} {} }}\n".format(*Hmin, *Hmax, n)
        mif += "    {{ {} {} {} {} {} {} {} }}\n".format(*Hmax, *Hmin, n)
        mif += "  }\n"
        mif += "}\n\n"
        mif += "# CGEvolver\n"
        mif += "Specify Oxs_CGEvolve {}\n\n"
        mif += "# MinDriver\n"
        mif += "Specify Oxs_MinDriver {\n"
        mif += "  evolver Oxs_CGEvolve\n"
        mif += "  stopping_mxHxm 0.01\n"
        mif += "  mesh :{}\n".format(meshname)
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
        mif += "Destination mags mmArchive\n\n"
        mif += "Schedule DataTable table Stage 1\n"
        mif += "Schedule Oxs_MinDriver::Magnetization mags Stage 1"

        return mif

    def _check_args(self, **kwargs):
        Hmin = kwargs["Hmin"]
        Hmax = kwargs["Hmax"]
        n = kwargs["n"]

        if len(Hmin) != 3:
            raise ValueError("Expected length 3 tuple")
        if len(Hmax) != 3:
            raise ValueError("Expected length 3 tuple")
        if n <= 0 or not isinstance(n, int):
            raise ValueError("Expected n > 0.")
