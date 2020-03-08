import oommfc as oc
import discretisedfield as df
import micromagneticmodel as mm


def test_skyrmion():
    name = 'skyrmion'

    Ms = 1.1e6
    A = 1.6e-11
    D = 4e-3
    K = 0.51e6
    u = (0, 0, 1)
    H = (0, 0, 2e5)

    p1 = (-50e-9, -50e-9, 0)
    p2 = (50e-9, 50e-9, 10e-9)
    cell = (5e-9, 5e-9, 5e-9)
    region = df.Region(p1=p1, p2=p2)
    mesh = df.Mesh(p1=p1, p2=p2, cell=cell)

    system = mm.System(name=name)
    system.energy = (mm.Exchange(A=A) + mm.DMI(D=D, crystalclass='Cnv') +
                     mm.UniaxialAnisotropy(K=K, u=u) + mm.Demag() +
                     mm.Zeeman(H=H))

    def Ms_fun(pos):
        x, y, z = pos
        if (x**2 + y**2)**0.5 < 50e-9:
            return Ms
        else:
            return 0

    def m_init(pos):
        x, y, z = pos
        if (x**2 + y**2)**0.5 < 10e-9:
            return (0, 0.1, -1)
        else:
            return (0, 0.1, 1)

    system.m = df.Field(mesh, dim=3, value=m_init, norm=Ms_fun)

    md = oc.MinDriver()
    md.drive(system)

    # Check the magnetisation at the sample centre.
    value = system.m((0, 0, 0))
    assert value[2]/Ms < -0.97

    # Check the magnetisation at the sample edge.
    value = system.m((50e-9, 0, 0))
    assert value[2]/Ms > 0.5
