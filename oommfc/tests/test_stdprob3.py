import numpy as np
import oommfc as oc
import discretisedfield as df
import micromagneticmodel as mm
from scipy.optimize import bisect  # This is why scipy is a dependency.


def test_stdprob3():
    name = 'stdprob3'

    # Function for initiaising the flower state.
    def m_init_flower(pos):
        x, y, z = pos[0]/1e-9, pos[1]/1e-9, pos[2]/1e-9
        mx = 0
        my = 2*z - 1
        mz = -2*y + 1
        norm_squared = mx**2 + my**2 + mz**2
        if norm_squared <= 0.05:
            return (1, 0, 0)
        else:
            return (mx, my, mz)

    # Function for initialising the vortex state.
    def m_init_vortex(pos):
        x, y, z = pos[0]/1e-9, pos[1]/1e-9, pos[2]/1e-9
        mx = 0
        my = np.sin(np.pi/2 * (x-0.5))
        mz = np.cos(np.pi/2 * (x-0.5))

        return (mx, my, mz)

    def minimise_system_energy(L, m_init):
        N = 16  # discretisation in one dimension
        cubesize = 100e-9  # cube edge length (m)
        cellsize = cubesize/N  # discretisation in all three dimensions.
        lex = cubesize/L  # exchange length.

        Km = 1e6  # magnetostatic energy density (J/m**3)
        Ms = np.sqrt(2*Km/mm.consts.mu0)  # magnetisation saturation (A/m)
        A = 0.5 * mm.consts.mu0 * Ms**2 * lex**2  # exchange energy constant
        K = 0.1*Km  # Uniaxial anisotropy constant
        u = (0, 0, 1)  # Uniaxial anisotropy easy-axis

        p1 = (0, 0, 0)  # Minimum sample coordinate.
        p2 = (cubesize, cubesize, cubesize)  # Maximum sample coordinate.
        cell = (cellsize, cellsize, cellsize)  # Discretisation.
        region = df.Region(p1=p1, p2=p2)
        mesh = df.Mesh(region=region, cell=cell)

        system = mm.System(name=name)
        system.energy = (mm.Exchange(A=A) + mm.UniaxialAnisotropy(K=K, u=u) +
                         mm.Demag())
        system.m = df.Field(mesh, dim=3, value=m_init, norm=Ms)

        md = oc.MinDriver()
        md.drive(system)

        return system

    def energy_difference(L):
        vortex = minimise_system_energy(L, m_init_vortex)
        flower = minimise_system_energy(L, m_init_flower)

        Evortex = vortex.table.tail(1)['E'][0]
        Eflower = flower.table.tail(1)['E'][0]

        return Evortex - Eflower

    cross_section = bisect(energy_difference, 8, 9, xtol=0.1)
    assert 8.4 < cross_section < 8.5
