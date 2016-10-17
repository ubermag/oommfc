import os
import subprocess
import textwrap


class OOMMF:
    def __init__(self):
        self.test_oommf()

    def getenv(self, varname):
        """
        Gets value from the environment variable varname.

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

    def docker_available(self):
        try:
            subprocess.check_call(["docker", "version"])
        except subprocess.CalledProcessError:
            return False
        else:
            return True

    def test_oommf(self):
        try:
            self.oommfpath = self.getenv("OOMMFTCL")
        except EnvironmentError:
            self.host, self.docker = False, self.docker_available()
        else:
            if os.path.isfile(self.oommfpath):
                self.host, self.docker = True, False
            else:
                self.host, self.docker = False, True

        if not (self.host or self.docker):
            raise EnvironmentError("Neither Docker nor oommf are installed.")
                              
    def call_oommf(self, argstr):
        print("Calling OOMMF")
        if self.host:
            self._call_oommf_host(argstr)
        elif self.docker:
            self._call_oommf_docker(argstr)

    def _call_oommf_host(self, argstr):
        cmd = ("tclsh {} boxsi +fg {} "
               "-exitondone 1").format(os.getenv("OOMMFTCL"), argstr)
        print("Running OOMMF on the host machine...")
        out = subprocess.call(cmd, shell=True)
        if out:
            raise EnvironmentError("Error in OOMMF run.")
        else:
            print("Completed OOMMF simulation on the host machine.")

    def _call_oommf_docker(self, argstr):
        print("Pull OOMMF docker image...")
        out = subprocess.call(["docker", "pull", "joommf/oommf"])
        if out:
            raise EnvironmentError("Cannot pull OOMMF docker image.")
        print("Running OOMMF in Docker container...")
        cmd = ("docker run -v {}:/io joommf/oommf "
               "/bin/bash -c \"tclsh /usr/local/oommf/oommf/oommf.tcl "
               "boxsi +fg {} -exitondone 1\"").format(os.getcwd(), argstr)
        out = subprocess.call(cmd, shell=True)
