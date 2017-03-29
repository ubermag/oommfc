import oommfc as oc
import discretisedfield as df


def bar():
    system = oc.System(name="example-bar")
    shape = (100e-9, 30e-9, 30e-9)
    d = 10e-9
    mesh = oc.Mesh(p1=(0, 0, 0), p2=shape, cell=(d, d, d))
    # Permalloy
    A = 1e-12
    H = (0, 0, 0)  # no Zeeman field, but provide interaction as convenience

    system.hamiltonian = oc.Exchange(A=A) + oc.Demag() + oc.Zeeman(H=H)
    alpha = 0.2
    system.dynamics = oc.Precession(gamma=oc.gamma0) + oc.Damping(alpha=alpha)
    Ms = 8e6  # A/m
    system.m = df.Field(mesh, value=(1, 0, 1), norm=Ms)

    return system
