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
            print(100*'**')
            return os.getenv(varname)


    def test_oommf(self):
        try:
            self.oommfpath = self.oommf_path("OOMMFTCL")
        except EnvironmentError:
            self.host, self.docker = False, installed("docker")
        else:
            if os.path.isfile(self.oommfpath):
                self.host, self.docker = True, False
            else:
                self.host, self.docker = False, True

        if not (self.host or self.docker):
            raise EnvironmentError("Neither Docker nor oommf are installed.")
                              
    def call_oommf(self, argstring):
        if self.host:
            cmd = ["tclsh", os.getenv("OOMMFTCL"), argstring,
                   "-exitondone", "1"]
            process = subprocess.Popen(cmd,
                                       stdout=subprocess.PIPE, 
                                       stderr=subprocess.PIPE)

            return process.communicate()
        elif self.docker:
            pass

    def version(self):
        out, err = self.call_oommf("+version")
        return err.decode().split("\n")[1].split()[1]
