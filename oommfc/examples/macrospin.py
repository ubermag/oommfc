import os
import time
import oommfc as oc
import discretisedfield as df


def macrospin():
    """Return a sytsem that represents a macrospin."""
    # define macro spin (i.e. one discretisation cell)
    p1 = (0, 0, 0)  # all lengths in metre
    p2 = (5e-9, 5e-9, 5e-9)
    cell = (5e-9, 5e-9, 5e-9)
    mesh = oc.Mesh(p1=p1, p2=p2, cell=cell)

    initial_m = (1, 0, 0)  # vector in x direction
    Ms = 8e6  # magnetisation saturation (A/m)
    m = df.Field(mesh, value=initial_m, norm=Ms)

    zeeman = oc.Zeeman(H=(0, 0, 5e6))  # external magnetic field (A/m)

    gamma = 2.211e5  # gyrotropic ratio
    alpha = 0.05  # Gilbert damping

    runid = "example-macrospin"
    system = oc.System(name=runid)
    system.hamiltonian = zeeman
    system.m = m
    system.dynamics = oc.Precession(gamma) + oc.Damping(alpha)

    return system
