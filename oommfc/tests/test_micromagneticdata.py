import discretisedfield as df
import micromagneticdata as mdata
import micromagneticmodel as mm
import numpy as np
import pytest
from micromagneticdata.testing.drive import *  # noqa: F403

import oommfc as oc


def rectangle(dirname, mode):
    """Simple rectangular ferromagnetic sample in external magnetic field."""
    print(">>> Running ferromagnetic rectangular cuboid")
    p1 = (-50e-9, -25e-9, 0)
    p2 = (50e-9, 25e-9, 20e-9)
    cell = (5e-9, 5e-9, 5e-9)

    region = df.Region(p1=p1, p2=p2)
    # use the region also as subregion: discretisedfield will create the additional
    # subregions json file and we can detect misalignment (translation) of the
    # region from the calculators (e.g. Mumax3 always defines pmin at the origin)
    mesh = df.Mesh(region=region, cell=cell, subregions={"total": region})

    Ms = 8e5
    A = 1.3e-11
    H = (1e6, 0.0, 2e5)
    alpha = 0.02

    system = mm.System(name="rectangle")
    system.energy = mm.Exchange(A=A) + mm.Zeeman(H=H)
    system.dynamics = mm.Precession(gamma0=mm.consts.gamma0) + mm.Damping(alpha=alpha)
    system.m = df.Field(mesh, nvdim=3, value=(0.0, 0.25, 0.1), norm=Ms)

    if mode == "time_drive":
        td = oc.TimeDriver()
        td.drive(system, t=25e-12, n=25, dirname=dirname)
    elif mode == "min_drive":
        md = oc.MinDriver()
        md.drive(system, dirname=dirname)
    elif mode == "min_drive_steps":
        md = oc.MinDriver()
        md.drive(system, output_step=True, dirname=dirname)
    else:
        raise NotImplementedError(mode)

    return system


def hysteresis(dirname, *args):
    """Hysteresis of a magnetic sphere with excange, uniaxial anisotropy and DMI."""
    print(">>> Running hysteresis simulation")
    region = df.Region(p1=(-50e-9, -50e-9, -50e-9), p2=(50e-9, 50e-9, 50e-9))
    mesh = df.Mesh(region=region, cell=(5e-9, 5e-9, 5e-9))

    system = mm.System(name="hysteresis")
    system.energy = (
        mm.Exchange(A=1e-12)
        + mm.UniaxialAnisotropy(K=4e5, u=(0, 0, 1))
        + mm.DMI(D=1e-3, crystalclass="T")
    )

    def Ms_fun(point):
        x, y, z = point
        if x**2 + y**2 + z**2 <= 50e-9**2:
            return 1e6
        else:
            return 0

    system.m = df.Field(mesh, nvdim=3, value=(0, 0, -1), norm=Ms_fun)

    Hmin = (0, 0, -1 / mm.consts.mu0)
    Hmax = (0, 0, 1 / mm.consts.mu0)

    hd = oc.HysteresisDriver()
    hd.drive(system, Hmin=Hmin, Hmax=Hmax, n=21, dirname=dirname)

    return system


@pytest.fixture(
    scope="session",
    params=[
        (
            rectangle,
            ("min_drive",),
            ("iteration", "mx", "Schedule Oxs_MinDriver::Magnetization mags Stage 1"),
        ),
        (
            rectangle,
            ("min_drive_steps",),
            ("iteration", "mx", "Schedule Oxs_MinDriver::Magnetization mags Step 1"),
        ),
        (
            rectangle,
            ("time_drive",),
            ("t", "mx", "Schedule Oxs_TimeDriver::Magnetization mags Stage 1"),
        ),
        (hysteresis, ("",), ("B_hysteresis", "mx", "Hrange")),
    ],
)
def _compute(tmp_path_factory, request):
    # compute test data once and reuse for all tests; separate public fixtures to create
    # a new drive object per test/fixture call to ensure tests stay independent
    callback, args, reference = request.param
    dirname = tmp_path_factory.mktemp(callback.__name__ + args[0])
    system = callback(dirname, *args)
    return system.name, system.drive_number - 1, dirname, reference


@pytest.fixture
def drive_with_reference(_compute):
    name, number, dirname, reference = _compute
    return mdata.Drive(name=name, number=number, dirname=dirname), reference


@pytest.fixture
def drive(_compute):
    name, number, dirname, _ = _compute
    return mdata.Drive(name=name, number=number, dirname=dirname)


# Additional oommf specific tests


def test_ovf2vtk(drive, tmp_path):
    drive.ovf2vtk(dirname=tmp_path)


def test_to_xarray_hysteresis(tmp_path):
    system = hysteresis(tmp_path)
    drive = mdata.Drive(
        name=system.name, number=system.drive_number - 1, dirname=tmp_path
    )
    assert all(
        np.allclose(
            drive.to_xarray()[f"B{i}_hysteresis"].values,
            drive.table.data[f"B{i}_hysteresis"].to_numpy(),
        )
        for i in "xyz"
    )
