import os
import shutil
import oommfc as oc
import discretisedfield as df
import micromagneticmodel as mm


def test_multiple_runs():
    name = 'multiple_runs'

    p1 = (0, 0, 0)
    p2 = (5e-9, 5e-9, 5e-9)
    n = (2, 2, 2)
    Ms = 1e6
    A = 1e-12
    H = (0, 0, 1e6)
    region = df.Region(p1=p1, p2=p2)
    mesh = df.Mesh(region=region, n=n)

    system = mm.System(name=name)
    system.energy = mm.Exchange(A=A) + mm.Zeeman(H=H)
    system.dynamics = (mm.Precession(gamma0=mm.consts.gamma0) +
                       mm.Damping(alpha=1))
    system.m = df.Field(mesh, dim=3, value=(0, 0.1, 1), norm=Ms)

    md = oc.MinDriver()
    md.drive(system, save=True, overwrite=True)

    dirname = os.path.join(name, 'drive-0')
    assert os.path.exists(dirname)

    system.energy.zeeman.H = (1e6, 0, 0)

    td = oc.TimeDriver()
    td.drive(system, t=100e-12, n=10, save=True)

    dirname = os.path.join(name, 'drive-1')
    assert os.path.exists(dirname)

    oc.delete(system)
