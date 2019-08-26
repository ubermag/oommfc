import os
import shutil
import oommfc as oc
import discretisedfield as df


def test_multiple_runs():
    name = 'multiple_runs'
    if os.path.exists(name):
        shutil.rmtree(name)

    p1 = (0, 0, 0)
    p2 = (5e-9, 5e-9, 5e-9)
    n = (2, 2, 2)
    Ms = 1e6
    A = 1e-12
    H = (0, 0, 1e6)
    mesh = oc.Mesh(p1=p1, p2=p2, n=n)

    system = oc.System(name=name)
    system.hamiltonian = oc.Exchange(A=A) + oc.Zeeman(H=H)
    system.dynamics = oc.Precession(gamma=oc.consts.gamma0) + \
        oc.Damping(alpha=1)
    system.m = df.Field(mesh, dim=3, value=(0, 0.1, 1), norm=Ms)

    md = oc.MinDriver()
    md.drive(system)

    dirname = os.path.join(name, 'drive-0')
    assert os.path.exists(dirname)

    system.hamiltonian.zeeman.H = (1e6, 0, 0)

    td = oc.TimeDriver()
    td.drive(system, t=100e-12, n=10)

    dirname = os.path.join(name, 'drive-1')
    assert os.path.exists(dirname)

    system.delete()
