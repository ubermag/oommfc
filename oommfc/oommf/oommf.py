import os
import signal
import subprocess


# Default values
varname = "OOMMFTCL"
dockername = "docker"


def status(varname=varname, dockername=dockername, raise_exception=False):
    # OOMMF status on host
    returncode = call_host("+v", varname=varname)
    if not returncode:
        print("OOMMF on host machine status: OK")
        host = True
    else:
        host = False
        # Investigate the reason why OOMMF does not run.
        oommfpath = os.getenv(varname)
        if oommfpath is None:
            print("Cannot find {} path.".format(varname))
        else:
            if os.path.isfile(oommfpath):
                print("{} path {} set to an existing "
                      "file.".format(varname, oommfpath))
                print("Something wrong with OOMMF installation.")
            else:
                print("{} path {} set to a non-existing "
                      "file.".format(oommfpath))

    # Docker status
    try:
        subprocess.check_call([dockername, "--version"])
    except (subprocess.CalledProcessError, FileNotFoundError):
        docker = False
        print("Docker not installed/active.")
    else:
        print("Docker status: OK")
        docker = True

    # Raise exception if required
    if not (host or docker) and raise_exception:
        raise EnvironmentError("OOMMF and docker not found.")

    return {"host": host, "docker": docker}


def call(argstr, where=None, varname=varname):
    where = where_to_run(where)

    if status(raise_exception=True)[where]:
        if where == "host":
            return call_host(argstr)
        elif where == "docker":
            return call_docker(argstr)


def version(where=None, varname=varname):
    where = where_to_run(where)
    if where == "host":
        cmd = ("tclsh", os.getenv(varname), "+version")
        phost = subprocess.Popen(cmd, stderr=subprocess.PIPE)
        out, err = phost.communicate()
    else:
        returncode = subprocess.call(["docker", "pull", "joommf/oommf"])
        cmd = ("docker run -v {}:/io joommf/oommf "
               "/bin/bash -c \"tclsh /usr/local/oommf/oommf/oommf.tcl "
               "+version\"").format(os.getcwd())
        pdocker = subprocess.Popen(cmd, shell=True, stderr=subprocess.PIPE)
        out, err = pdocker.communicate()

    return err.decode().split("oommf.tcl")[-1].strip()


def where_to_run(where, varname=varname):
    oommf_status = status(raise_exception=True, varname=varname)
    if where is None:
        if oommf_status["host"]:
            return "host"
        else:
            return "docker"
    else:
        return where


def call_host(argstr, varname=varname):
    cmd = ("tclsh", os.getenv(varname, "None"),
           "boxsi", "+fg", argstr, "-exitondone", "1")
    return subprocess.call(cmd)


def call_docker(argstr, dockerhubimage="joommf/oommf"):
    returncode = subprocess.call(["docker", "pull", dockerhubimage])
    cmd = ("docker run -v {}:/io {} /bin/bash -c \"tclsh "
           "/usr/local/oommf/oommf/oommf.tcl boxsi +fg {} "
           "-exitondone 1\"").format(os.getcwd(), dockerhubimage, argstr)
    return subprocess.call(cmd, shell=True)
