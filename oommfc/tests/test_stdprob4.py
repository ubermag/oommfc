import oommfc as oc
import discretisedfield as df
import micromagneticmodel as mm


def test_stdprob4():
    name = 'stdprob4'

    L, d, th = 500e-9, 125e-9, 3e-9   # (m)
    cell = (5e-9, 5e-9, 3e-9)  # (m)
    p1 = (0, 0, 0)
    p2 = (L, d, th)
    region = df.Region(p1=p1, p2=p2)
    mesh = df.Mesh(region=region, cell=cell)

    Ms = 8e5  # (A/m)
    A = 1.3e-11  # (J/m)

    system = mm.System(name=name)
    system.energy = mm.Exchange(A=A) + mm.Demag()

    gamma0 = 2.211e5  # (m/As)
    alpha = 0.02
    system.dynamics = mm.Precession(gamma0=gamma0) + mm.Damping(alpha=alpha)

    system.m = df.Field(mesh, dim=3, value=(1, 0.25, 0.1), norm=Ms)

    md = oc.MinDriver()
    md.drive(system)  # updates system.m in-place

    H = (-24.6e-3/mm.consts.mu0, 4.3e-3/mm.consts.mu0, 0)
    system.energy += mm.Zeeman(H=H)

    td = oc.TimeDriver()
    td.drive(system, t=1e-9, n=200)

    t = system.table['t'].values
    my = system.table['my'].values

    assert abs(min(t) - 5e-12) < 1e-20
    assert abs(max(t) - 1e-9) < 1e-20

    # Eye-norm test.
    assert 0.7 < max(my) < 0.8
    assert -0.5 < min(my) < -0.4
