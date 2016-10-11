import os
import subprocess


class OOMMF:
    def installed(self, package="oommf"):
        try:
            subprocess.check_call(["which", package])
        except subprocess.CalledProcessError:
            return False
        else:
            return True

    def environment_variable(self, varname="OOMMFTCL"):
        if not os.getenv(varname, False):
            return False
        else:
            return True

    def test_oommf(self):
        if not self.installed():
            raise Exception("OOMMF is not installed.")
        elif not self.environment_variable():
            raise Exception("OOMMFTCL environment variable not set.")
        else:
            return True

    def call_oommf(self, argstring):
        cmd = ["tclsh", os.getenv("OOMMFTCL"), argstring]
        process = subprocess.Popen(cmd,
                                   stdout=subprocess.PIPE, 
                                   stderr=subprocess.PIPE)

        return process.communicate()

    def version(self):
        if self.test_oommf():
            out, err = self.call_oommf("+version")

            return err.decode().split("\n")[1].split()[1]
