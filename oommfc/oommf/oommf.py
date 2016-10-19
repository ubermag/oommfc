import os
import subprocess


def status(raise_exception=False):
    # OOMMF status on host
    returncode = call_host("+version")
    if not returncode:
        print("OOMMF on host machine status: OK")
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
        print("Docker status: OK")
        docker = True

    # Raise exception if required
    if not (host or docker) and raise_exception:
        raise EnvironmentError("OOMMF and docker not found.")

    return {"host": host, "docker": docker}


def call(argstr, where=None):
    where = where_to_run(where)

    if status(raise_exception=True)[where]:
        if where == "host":
            return call_host(argstr)
        elif where == "docker":
            return call_docker(argstr)


def where_to_run(where):
    oommf_status = status(raise_exception=True)
    if where is None:
        if oommf_status["host"]:
            return "host"
        else:
            return "docker"
    else:
        return where


def call_host(argstr):
    cmd = ("tclsh", os.getenv("OOMMFTCL", "None"),
           "boxsi", "+fg", argstr, "-exitondone", "1")
    return subprocess.call(cmd)


def call_docker(argstr):
    returncode = subprocess.call(["docker", "pull", "joommf/oommf"])
    cmd = ("docker run -v {}:/io joommf/oommf "
           "/bin/bash -c \"tclsh /usr/local/oommf/oommf/oommf.tcl "
           "boxsi +fg {} -exitondone 1\"").format(os.getcwd(), argstr)
    return subprocess.call(cmd, shell=True)
