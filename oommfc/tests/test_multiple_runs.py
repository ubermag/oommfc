import os
import glob
import shutil
import pytest
import oommfc as oc
import discretisedfield as df
import pytest


@pytest.mark.oommf
def test_multiple_runs():
    name = "multiple_runs"

    # Remove any previous simulation directories.
    if os.path.exists(name):
        shutil.rmtree(name)

    L = 10e-9   # (m)
    cellsize = (5e-9, 5e-9, 5e-9)  # (m)
    mesh = oc.Mesh((0, 0, 0), (L, L, L), cellsize)

    system = oc.System(name=name)

    A = 1.3e-11  # (J/m)
    system.hamiltonian = oc.Exchange(A)

    gamma = 2.211e5  # (m/As)
    alpha = 0.02
    system.dynamics = oc.Precession(gamma) + oc.Damping(alpha)

    Ms = 8e5  # (A/m)
    system.m = df.Field(mesh, value=(1, 0.25, 0.1), norm=Ms)

    md = oc.MinDriver()
    md.drive(system)  # updates system.m in-place

    
    dirname = os.path.join(name, "")
    subdirname =  os.path.join(dirname, 'run-0')
    miffilename = os.path.join(subdirname, "{}.mif".format(name))
    assert os.path.exists(dirname)
    assert os.path.exists(subdirname)
    assert os.path.isfile(miffilename)


    mif_file  = list(glob.iglob("{}/*.mif".format(subdirname)))
    omf_files = list(glob.iglob("{}/*.omf".format(subdirname)))
    odt_files = list(glob.iglob("{}/*.odt".format(subdirname)))

    assert len(mif_file) == 1
    assert len(omf_files) > 1
    omffilename = os.path.join(subdirname, "m0.omf")
    assert omffilename in omf_files

    assert len(odt_files) >= 1
