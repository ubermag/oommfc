import os
import signal
import subprocess


def status(varname, dockername, raise_exception):
    # OOMMF status on host
    returncode = call_host(varname=varname, argstr="+version")
    if not returncode:
        host = True
    else:
        host = False
        # Investigate the reason why OOMMF does not run.
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

    # Docker status
    try:
        subprocess.check_call([dockername, "--version"])
    except (subprocess.CalledProcessError, FileNotFoundError):
        docker = False
        print("Docker not installed/active.")
    else:
        docker = True

    # Raise exception if required
    if not (host or docker) and raise_exception:
        raise EnvironmentError("OOMMF and docker not found.")

    return {"host": host, "docker": docker}


def call(argstr, varname, dockername, raise_exception, dockerimage, where=None):
    where = where_to_run(where, varname, dockername, raise_exception)

    if status(varname=varname, dockername=dockername,
              raise_exception=raise_exception)[where]:
        if where == "host":
            return call_host(varname=varname, argstr=argstr)
        elif where == "docker":
            return call_docker(dockername=dockername, dockerimage=dockerimage,
                               argstr=argstr)


def version(where=None, varname="OOMMFTCL", dockerimage="joommf/oommf"):
    where = where_to_run(where=where, varname=varname,
                         dockername="docker",
                         raise_exception=True)
    if where == "host":
        cmd = ("tclsh", os.getenv(varname), "+version")
        phost = subprocess.Popen(cmd, stderr=subprocess.PIPE)
        out, err = phost.communicate()
    else:
        returncode = subprocess.call(["docker", "pull", "joommf/oommf"])
        cmd = ("docker run --privileged -v {}:/io {} "
               "/bin/bash -c \"tclsh /usr/local/oommf/oommf/oommf.tcl "
               "+version\"").format(os.getcwd(), dockerimage)
        pdocker = subprocess.Popen(cmd, shell=True, stderr=subprocess.PIPE)
        out, err = pdocker.communicate()

    return err.decode().split("oommf.tcl")[-1].strip()


def where_to_run(where, varname, dockername, raise_exception):
    oommf_status = status(varname=varname, dockername=dockername,
                          raise_exception=raise_exception)
    if where is None:
        if oommf_status["host"]:
            return "host"
        else:
            return "docker"
    else:
        return where


def call_host(varname, argstr):
    cmd = ("tclsh", os.getenv(varname, "None"),
           "boxsi", "+fg", argstr, "-exitondone", "1")
    return subprocess.call(cmd)


def call_docker(dockername, dockerimage, argstr):
    returncode = subprocess.call([dockername, "pull", dockerimage])
    cmd = ("{} run -v {}:/io {} /bin/bash -c \"tclsh "
           "/usr/local/oommf/oommf/oommf.tcl boxsi +fg {} "
           "-exitondone 1\"").format(dockername, os.getcwd(),
                                     dockerimage, argstr)
    return subprocess.call(cmd, shell=True)
