from .driver import Driver


class MinDriver(Driver):
    def _script(self, system):
        meshname = system.m.mesh.name
        systemname = system.name

        mif = "# m0 file\n"
        mif += "Specify Oxs_FileVectorField:m0file {\n"
        mif += "   atlas :atlas\n"
        mif += "   file m0.omf\n"
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
        pass
