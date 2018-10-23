import os
import glob
import json
import shutil
import pytest
import oommfc as oc
import discretisedfield as df
import pytest


@pytest.mark.oommf
def test_multiple_runs():
    name = "info_file"

    # Remove any previous simulation directories.
    if os.path.exists(name):
        shutil.rmtree(name)

    L = 30e-9   # (m)
    cellsize = (10e-9, 15e-9, 5e-9)  # (m)
    mesh = oc.Mesh((0, 0, 0), (L, L, L), cellsize)

    system = oc.System(name=name)

    A = 1.3e-11  # (J/m)
    H = (1e6, 0.0, 2e5)
    system.hamiltonian = oc.Exchange(A=A) + oc.Zeeman(H=H)

    gamma = 2.211e5  # (m/As)
    alpha = 0.02
    system.dynamics = oc.Precession(gamma) + oc.Damping(alpha)

    Ms = 8e5  # (A/m)
    system.m = df.Field(mesh, value=(0.0, 0.25, 0.1), norm=Ms)

    td = oc.TimeDriver()
    td.drive(system, t=25e-12, n=10)  # updates system.m in-place
    
    dirname = os.path.join(name, "run-0")
    infofile = os.path.join(dirname, "info.json")
    assert os.path.exists(dirname)
    assert os.path.isfile(infofile)

    shutil.rmtree(name)
