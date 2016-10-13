import os
import glob
import oommfc as oc
import discretisedfield as df


def test_stdprob4():
    name = "stdprob4"

    # Remove any previous simulation directories.
    os.system("rm -rf {}/".format(name))

    L, d, th = 500e-9, 125e-9, 3e-9   # (m)
    cellsize = (5e-9, 5e-9, 3e-9)  # (m)
    mesh = oc.Mesh((0, 0, 0), (L, d, th), cellsize)

    system = oc.System(name=name)
    system.mesh = mesh

    A = 1.3e-11  # (J/m)
    system.hamiltonian = oc.Exchange(A) + oc.Demag()

    gamma = 2.211e5  # (m/As)
    alpha = 0.02
    system.dynamics = oc.Precession(gamma) + oc.Damping(alpha)

    Ms = 8e5  # (A/m)
    system.m = df.Field(mesh, value=(1, 0.25, 0.1),
                        normalisedto=Ms)

    md = oc.MinDriver()
    md.drive(system)  # updates system.m in-place

    assert os.path.exists("{}/".format(name))
    assert os.path.isfile("{}/{}.mif".format(name, name))

    omf_files = list(glob.iglob("{}/*.omf".format(name)))
    odt_files = list(glob.iglob("{}/*.odt".format(name)))

    assert len(omf_files) == 2
    assert "{}/m0.omf".format(name) in omf_files

    assert len(odt_files) == 1

    os.system("rm -r {}/".format(name))

    H = (-24.6e-3/oc.mu0, 4.3e-3/oc.mu0, 0)
    system.hamiltonian += oc.Zeeman(H)

    td = oc.TimeDriver()
    td.drive(system, t=1e-9, n=200)

    assert os.path.exists("{}/".format(name))
    assert os.path.isfile("{}/{}.mif".format(name, name))

    omf_files = list(glob.iglob("{}/*.omf".format(name)))
    odt_files = list(glob.iglob("{}/*.odt".format(name)))

    assert len(omf_files) == 201
    assert "{}/m0.omf".format(name) in omf_files

    assert len(odt_files) == 1

    myplot = system.dt.plot("t", "my")
    myplot.figure.savefig("{}/stdprob4-t-my.pdf".format(name))

    assert os.path.isfile("{}/stdprob4-t-my.pdf".format(name))

    t = system.dt["t"].as_matrix()
    my = system.dt["my"].as_matrix()

    assert abs(min(t) - 5e-12) < 1e-20
    assert abs(max(t) - 1e-9) < 1e-20

    # Eye-norm test.
    assert 0.7 < max(my) < 0.8
    assert -0.5 < min(my) < -0.4

    os.system("rm -r {}/".format(name))
