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
    
    dirname = os.path.join(name, "drive-0")
    miffilename = os.path.join(dirname, "{}.mif".format(name))
    assert os.path.exists(dirname)
    assert os.path.isfile(miffilename)

    mif_file  = list(glob.iglob("{}/*.mif".format(dirname)))
    omf_files = list(glob.iglob("{}/*.omf".format(dirname)))
    odt_files = list(glob.iglob("{}/*.odt".format(dirname)))

    assert len(mif_file) == 1
    assert len(omf_files) > 1
    omffilename = os.path.join(dirname, "m0.omf")
    assert omffilename in omf_files

    assert len(odt_files) >= 1

    td = oc.TimeDriver()
    td.drive(system, t=100e-12, n=10)  # updates system.m in-place

    dirname = os.path.join(name, "drive-1")
    miffilename = os.path.join(dirname, "{}.mif".format(name))
    assert os.path.exists(dirname)
    assert os.path.isfile(miffilename)

    mif_file  = list(glob.iglob("{}/*.mif".format(dirname)))
    omf_files = list(glob.iglob("{}/*.omf".format(dirname)))
    odt_files = list(glob.iglob("{}/*.odt".format(dirname)))

    assert len(mif_file) == 1
    assert len(omf_files) == 11
    omffilename = os.path.join(dirname, "m0.omf")
    assert omffilename in omf_files

    assert len(odt_files) >= 1

    shutil.rmtree(name)
