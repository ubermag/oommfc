import os
import subprocess
import textwrap


class OOMMF:
    def __init__(self):
        self.test_oommf()

    def installed(self, package):
        """Checks if package is installed."""
        try:
            subprocess.check_call(["which", package])
        except subprocess.CalledProcessError:
            return False
        else:
            return True

    def oommf_path(self, varname="OOMMFTCL"):
        """
        Gets value from the environment variable varname.

        Returns
        -------
        string
          Path to folder containing oommf.tcl

        Notes
        -----
        Environment variable OOMMF_PATH should point to the directory which
        contains 'oommf.tcl'

        """
        if not varname in os.environ:
            msg = textwrap.dedent("""\
            Please set the OOMMFTCL environment variable to point to the
            directory that contains the file 'oommf.tcl'. In bash, you can
            write:
              export OOMMFTCL=/yourhome/yourpath/to/oommf
            This can be added to the ~/.bashrc, for example, to be executed
            automatically.
            Cowardly stopping here.
            """)
            raise EnvironmentError(msg)
        else:
            return os.getenv(varname)

    def test_oommf(self):
        try:
            self.oommfpath = self.oommf_path("OOMMFTCL")
        except EnvironmentError:
            self.host, self.docker = False, self.installed("docker")
        else:
            if os.path.isfile(self.oommfpath):
                self.host, self.docker = True, False
            else:
                self.host, self.docker = False, True

        if not (self.host or self.docker):
            raise EnvironmentError("Neither Docker nor oommf are installed.")
                              
    def call_oommf(self, argstring):
        print("Calling OOMMF")
        if self.host:
            cmd = ("tclsh {} boxsi +fg {} "
                   "-exitondone 1").format(os.getenv("OOMMFTCL"), argstring)
            print("Running OOMMF on the host machine...")
            out = os.system(cmd)
            if out:
                raise EnvironmentError("Error in OOMMF run.")
            else:
                print("Completed OOMMF simulation on the host machine.")

        elif self.docker:
            print("Pull OOMMF docker image...")
            out = os.system("docker pull joommf/oommf")
            if out:
                raise EnvironmentError("Cannot pull OOMMF docker image.")
            print("Running OOMMF in Docker container...")
            cmd = ("docker run -v {}:/io joommf/oommf "
                   "/bin/bash -c \"tclsh /usr/local/oommf/oommf/oommf.tcl "
                   "boxsi +fg {} -exitondone 1\"").format(os.getcwd(), argstring)
            print(cmd)
            out = os.system(cmd)
            #if not out:
            #    raise EnvironmentError("Error in OOMMF run inside Docker.")
            #else:
            #    print("OOMMF simulation inside Docker completed")
