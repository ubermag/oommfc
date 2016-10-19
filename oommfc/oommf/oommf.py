import os
import subprocess


class OOMMF:
    def status(self, raise_exception=False):
        # OOMMF status on host
        returncode = self._call_host("+version")
        if not returncode:
            host = True
        else:
            host = False
            # Investigate the reason why OOMMF does not run.
            oommftcl = os.getenv("OOMMFTCL")
            if oommftcl is None:
                print("Cannot find OOMMFTCL path.")
            else:
                oommftcl_file = os.path.isfile(oommftcl)
                if oommftcl_file:
                    print("OOMMFTCL path {} set to "
                          "an existing file.".format(oommftcl))
                    print("Something wrong with OOMMF installation.")
                else:
                    print("OOMMFTCL path {} set to "
                          "a non-existing file.".format(oommftcl))

        # Docker status
        try:
            subprocess.check_call(["docker", "--version"])
        except subprocess.CalledProcessError:
            docker = False
            print("Docker not installed/active.")
        else:
            docker = True

        # Raise exception if required
        if not (host or docker) and raise_exception:
            raise EnvironmentError("OOMMF and docker not found.")

        return {"host": host, "docker": docker}
                              
    def call(self, argstr, where=None):
        where = self._where_to_run(where)

        if self.status(raise_exception=True)[where]:
            if where == "host":
                return self._call_host(argstr)
            elif where == "docker":
                return self._call_docker(argstr)

    def _where_to_run(self, where):
        oommf_status = self.status(raise_exception=True)
        if where is None:
            if oommf_status["host"]:
                return "host"
            else:
                return "docker"
        else:
            return where

    def _call_host(self, argstr):
        cmd = ("tclsh", os.getenv("OOMMFTCL", "None"),
               "boxsi", "+fg", argstr, "-exitondone", "1")
        return subprocess.call(cmd)

    def _call_docker(self, argstr):
        returncode = subprocess.call(["docker", "pull", "joommf/oommf"])
        cmd = ("docker run -v {}:/io joommf/oommf "
               "/bin/bash -c \"tclsh /usr/local/oommf/oommf/oommf.tcl "
               "boxsi +fg {} -exitondone 1\"").format(os.getcwd(), argstr)
        return subprocess.call(cmd, shell=True)
