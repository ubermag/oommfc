import os
import glob
import shutil
import pytest
import oommfc as oc
import discretisedfield as df
import pytest


def test_stdprob4():
    name = 'stdprob4'

    # Remove any previous simulation directories.
    if os.path.exists(name):
        shutil.rmtree(name)

    L, d, th = 500e-9, 125e-9, 3e-9   # (m)
    cell = (5e-9, 5e-9, 3e-9)  # (m)
    mesh = oc.Mesh(p1=(0, 0, 0), p2=(L, d, th), cell=cell)

    Ms = 8e5  # (A/m)
    A = 1.3e-11  # (J/m)

    system = oc.System(name=name)

    system.hamiltonian = oc.Exchange(A=A) + oc.Demag()

    gamma = 2.211e5  # (m/As)
    alpha = 0.02
    system.dynamics = oc.Precession(gamma=gamma) + \
        oc.Damping(alpha=alpha)

    system.m = df.Field(mesh, value=(1, 0.25, 0.1), norm=Ms)

    md = oc.MinDriver()
    md.drive(system)  # updates system.m in-place

    H = (-24.6e-3/oc.consts.mu0, 4.3e-3/oc.consts.mu0, 0)
    system.hamiltonian += oc.Zeeman(H)

    td = oc.TimeDriver()
    td.drive(system, t=1e-9, n=200)

    t = system.dt['t'].values
    my = system.dt['my'].values

    assert abs(min(t) - 5e-12) < 1e-20
    assert abs(max(t) - 1e-9) < 1e-20

    # Eye-norm test.
    assert 0.7 < max(my) < 0.8
    assert -0.5 < min(my) < -0.4

    system.delete()
