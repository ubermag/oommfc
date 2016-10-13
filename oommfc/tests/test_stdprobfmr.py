import os
import glob
import scipy.fftpack
import numpy as np
import oommfc as oc
import discretisedfield as df


def test_stdprobfmr():
    name = "stdprobfmr"

    # Remove any previous simulation directories.
    os.system("rm -rf {}/".format(name))

    lx = ly = 120e-9  # x and y dimensions of the sample(m)
    lz = 10e-9  # sample thickness (m)
    dx = dy = dz = 10e-9  # discretisation in x, y, and z directions (m)

    Ms = 8e5  # saturation magnetisation (A/m)
    A = 1.3e-11  # exchange energy constant (J/m)
    H = 8e4 * np.array([0.81345856316858023, 0.58162287266553481, 0.0])
    alpha = 0.008  # Gilbert damping
    gamma = 2.211e5

    mesh = oc.Mesh(p1=(0, 0, 0), p2=(lx, ly, lz), cell=(dx, dy, dz))

    system = oc.System(name="stdprobfmr")

    system.mesh = mesh
    system.hamiltonian = oc.Exchange(A) + oc.Demag() + oc.Zeeman(H)
    system.dynamics = oc.Precession(gamma) + oc.Damping(alpha)
    system.m = df.Field(mesh, value=(0, 0, 1), normalisedto=Ms)

    md = oc.MinDriver()
    md.drive(system)

    H = 8e4 * np.array([0.81923192051904048, 0.57346234436332832, 0.0])
    system.hamiltonian.zeeman.H = H

    T = 20e-9
    n = 4000

    td = oc.TimeDriver()
    td.drive(system, t=T, n=n)

    t = system.dt['t'].as_matrix()
    my = system.dt['mx'].as_matrix()

    psd = np.log10(np.abs(scipy.fftpack.fft(my))**2)
    f_axis = scipy.fftpack.fftfreq(4000, d=20e-9/4000)

    os.system("rm -r {}/".format(name))
