from .driver import Driver


class HysteresisDriver(Driver):
    def script(self, system, **kwargs):
        meshname = system.mesh.name
        Ms = system.m.normalisedto
        systemname = system.name
        Hmin = kwargs["Hmin"]
        Hmax = kwargs["Hmax"]
        n = kwargs["n"]

        mif = "# UZeeman\n"
        mif += "Specify Oxs_UZeeman {\n"
        mif += "  Hrange {\n"
        mif += "    {{ {} {} {} {} {} {} {} }}\n".format(Hmin[0],
                                                         Hmin[1],
                                                         Hmin[2],
                                                         Hmax[0],
                                                         Hmax[1],
                                                         Hmax[2],
                                                         n)
        mif += "    {{ {} {} {} {} {} {} {} }}\n".format(Hmax[0],
                                                         Hmax[1],
                                                         Hmax[2],
                                                         Hmin[0],
                                                         Hmin[1],
                                                         Hmin[2],
                                                         n)
        mif += "  }\n"
        mif += "}\n\n"
        mif += "# CGEvolver\n"
        mif += "Specify Oxs_CGEvolve {}\n\n"
        mif += "# MinDriver\n"
        mif += "Specify Oxs_MinDriver {\n"
        mif += "  evolver Oxs_CGEvolve\n"
        mif += "  stopping_mxHxm 0.01\n"
        mif += "  mesh :{}\n".format(meshname)
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
        mif += "Schedule Oxs_MinDriver::Spin mags Stage 1"
        
        return mif
