import os
from .driver import Driver


class TimeDriver(Driver):
    def drive(self, system, t, n=1):
        """
        Drive the system using time driver.

        """
        filenames = self._filenames(system)

        # Make directory for saving OOMMF files.
        self._makedir(system)

        # Save system's magnetisation configuration omf file.
        omffilename = filenames["oommffilename"]
        system.m.write_oommf_file(omffilename)

        # Save OOMMF configuration mif file.
        miffilename = filenames["miffilename"]
        self._save_mif(system, t=t, n=n)

        # Run simulation.
        self._run_simulator(system)

        # Update system.
        self._update_system(system)

    def script(self, system, **kwargs):
        mif = "# RungeKuttaEvolver\n"
        mif += "Specify Oxs_RungeKuttaEvolve:evolver {\n"
        mif += "  alpha {}\n".format(system.dynamics.damping.alpha)
        mif += "  gamma_G {}\n".format(system.dynamics.precession.gamma)
        mif += "}\n\n"
        mif += "# TimeDriver\n"
        mif += "Specify Oxs_TimeDriver {\n"
        mif += "  evolver Oxs_RungeKuttaEvolve\n"
        mif += "  stopping_time {}\n".format(kwargs["t"])
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
        mif += "Schedule Oxs_MinDriver::Spin mags Stage 1"
        return mif
