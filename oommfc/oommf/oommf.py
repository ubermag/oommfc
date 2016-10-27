import os
import signal
import subprocess


class OOMMF:
    def __init__(self, varname="OOMMFTCL", dockername="docker",
                 dockerimage="joommf/oommf", where=None):
        self.varname = varname
        self.dockername = dockername
        self.dockerimage = dockerimage
        self.statusdict = self.status(raise_exception=False)
        self.where = self._where_to_run(where)

    def status(self, raise_exception=False, verbose=False):
        # OOMMF status on host
        oommfpath = os.getenv(self.varname, None)
        try:
            if oommfpath is None:
                raise FileNotFoundError
            else:
                cmd = ("tclsh", os.getenv(self.varname, None), "boxsi",
                       "+fg", "+version", "-exitondone", "1")
                subprocess.check_call(cmd, stdout=subprocess.PIPE)
        except (subprocess.CalledProcessError, FileNotFoundError):
            host = False
            if verbose:
                oommfpath = os.getenv(varname)
                if oommfpath is None:
                    print("Cannot find {} path.".format(varname))
                elif not os.path.isfile(oommfpath):
                    print("{} path {} set to a non-existing "
                          "file.".format(varname, oommfpath))
                else:
                    print("{} path {} set to an existing "
                          "file.".format(varname, oommfpath))
                    print("Something wrong with OOMMF installation.")
        else:
            host = True

        # Docker status
        try:
            cmd = (self.dockername, "images")
            subprocess.check_call(cmd)
        except (subprocess.CalledProcessError, FileNotFoundError):
            docker = False
            if verbose:
                print("Docker not installed/active.")
        else:
            docker = True

        # Raise exception if required
        if not (host or docker) and raise_exception:
            raise EnvironmentError("OOMMF and docker not found.")

        return {"host": host, "docker": docker}

    def call(self, argstr):
        if self.statusdict[self.where]:
            if self.where == "host":
                return self._call_host(argstr=argstr)
            elif self.where == "docker":
                return self._call_docker(argstr=argstr)

    def version(self, where=None):
        where = self._where_to_run(where=where)
        if where == "host":
            cmd = ("tclsh", os.getenv(self.varname), "+version")
            phost = subprocess.Popen(cmd, stderr=subprocess.PIPE)
            out, err = phost.communicate()
        else:
            returncode = subprocess.call([self.dockername,
                                          "pull",
                                          self.dockerimage])
            cmd = ("{} run --privileged -v {}:/io {} "
                   "/bin/bash -c \"tclsh /usr/local/oommf/oommf/oommf.tcl "
                   "+version\"").format(self.dockername, os.getcwd(),
                                        self.dockerimage)
            pdocker = subprocess.Popen(cmd,
                                       shell=True,
                                       stderr=subprocess.PIPE)
            out, err = pdocker.communicate()

        return err.decode().split("oommf.tcl")[-1].strip()

    def _where_to_run(self, where):
        if where is None:
            if self.statusdict["host"]:
                return "host"
            else:
                return "docker"
        else:
            return where

    def _call_host(self, argstr):
        oommfpath = os.getenv(self.varname, None)
        cmd = ("tclsh", oommfpath, "boxsi", "+fg",
               argstr, "-exitondone", "1")
        return subprocess.call(cmd)

    def _call_docker(self, argstr):
        returncode = subprocess.call([self.dockername, "pull",
                                      self.dockerimage])
        cmd = ("{} run -v {}:/io {} /bin/bash -c \"tclsh "
               "/usr/local/oommf/oommf/oommf.tcl boxsi +fg {} "
               "-exitondone 1\"").format(self.dockername, os.getcwd(),
                                         self.dockerimage, argstr)
        return subprocess.call(cmd, shell=True)
