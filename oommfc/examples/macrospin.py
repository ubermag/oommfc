import time
import oommfc as oc
import discretisedfield as df


def macrospin():
    """Return a sytsem that represents a macrospin.

    """
    p1 = (0, 0, 0)
    p2 = (5e-9, 5e-9, 5e-9)
    cell = (5e-9, 5e-9, 5e-9)
    mesh = oc.Mesh(p1=p1, p2=p2, cell=cell)

    system = oc.System(name="example-macrospin")
    system.hamiltonian = oc.Zeeman(H=(0, 0, 5e6))
    system.m = df.Field(mesh, value=(0, 0, 1), norm=8e6)
    system.dynamics = oc.Precession(gamma=oc.gamma) + oc.Damping(alpha=0.05)

    return system
