import discretisedfield as df
import micromagneticmodel as mm


def macrospin():
    name = 'example_macrospin'
    p1 = (0, 0, 0)
    p2 = (1e-9, 1e-9, 1e-9)
    n = (1, 1, 1)
    region = df.Region(p1=p1, p2=p2)
    mesh = df.Mesh(region=region, n=n)

    system = mm.System(name=name)
    system.energy = mm.Zeeman(H=(0, 0, 1e-9))
    system.dynamics = (mm.Precession(gamma0=mm.consts.gamma0) +
                       mm.Damping(alpha=0.1))
    system.m = df.Field(mesh, dim=3, value=(0, 1, 1), norm=1e6)

    return system
