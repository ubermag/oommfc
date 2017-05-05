import shutil
import pytest
import oommfc as oc
import discretisedfield as df


@pytest.mark.oommf
def test_stdprob1():
    name = "stdprob1"

    # Geometry
    lx = 2e-6  # x dimension of the sample(m)
    ly = 1e-6  # y dimension of the sample (m)
    lz = 20e-9  # sample thickness (m)

    # Material parameters
    Ms = 8e5  # saturation magnetisation (A/m)
    A = 1.3e-11  # exchange energy constant (J/m)
    K = 0.5e3  # uniaxial anisotropy constant (J/m**3)
    u = (1, 0, 0)  # uniaxial anisotropy axis

    # Create a mesh object.
    mesh = oc.Mesh(p1=(0, 0, 0), p2=(lx, ly, lz), cell=(20e-9, 20e-9, 20e-9))

    system = oc.System(name=name)
    system.hamiltonian = oc.Exchange(A) + oc.UniaxialAnisotropy(K, u) + \
        oc.Demag()
    system.m = df.Field(mesh, value=(-10, -1, 0), norm=Ms)

    Hmax = (50e-3/oc.mu0, 0.87275325e-3/oc.mu0, 0)
    Hmin = (-50e-3/oc.mu0, -0.87275325e-3/oc.mu0, 0)
    n = 10

    hd = oc.HysteresisDriver()
    hd.drive(system, Hmax=Hmax, Hmin=Hmin, n=n)

    Bx = system.dt["Bx"].as_matrix()
    mx = system.dt["mx"].as_matrix()

    assert len(mx) == 21
    assert len(Bx) == 21

    shutil.rmtree(name)
