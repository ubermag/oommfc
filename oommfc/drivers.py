"""
drivers.py

Drivers in OOMMF control the evolution of a simulation, iterating through time.
A driver controls the evolver, which performs the actual step through time or
phase space in the simulation.

For more detail consult the OOMMF Standard Oxs_Ext Child Classes documentation.
"""


class TimeDriver(object):

    """
    class TimeDriver(evolver, stopping_time, stage_count, mesh, Ms, m0,
                     basename='noname')

    The TimeDriver class is used for dynamic simulations - those where the aim
    is to look at how the system evolves over time.

    Input
    -----
    evolver:
        String, evolver name
    stopping_time:
        The time that a single stage lasts for.
    stage_count:
        The number of stages in a simulation - the total time simulated is
        the stage_count*stopping_time.
    mesh:
        String, the name of the mesh.
    Ms:
        Float, int, the saturation magnetization of the system in A/m.
    m0:
        List of length 3 or string describing initial magnetization.
    basename:
        Base file name which determines the start of the name of output files.
    """

    def __init__(self, evolver, stopping_time, stage_count,
                 mesh, Ms, m0, basename='noname'):
        if not isinstance(evolver, str):
            raise ValueError('evolver must be a string')
        else:
            self.evolver = evolver
        if not isinstance(stopping_time, (int, float)) or stopping_time <= 0:
            raise ValueError('stopping_time must be a positive float(int)')
        else:
            self.stopping_time = stopping_time
        if not isinstance(stage_count, int):
            raise ValueError('stage_count must be an int')
        else:
            self.stage_count = stage_count
        if not isinstance(mesh, str):
            raise ValueError('mesh must be a string')
        else:
            self.mesh = mesh
        if not isinstance(Ms, (float, int)) or Ms <= 0:
            raise ValueError('Ms must be a positive float(int).')
        else:
            self.Ms = Ms
        if not isinstance(m0, (list, tuple, str)):
            raise ValueError('m0 must be a string, list, or tuple.')
        else:
            self.m0 = m0
        if not isinstance(basename, str):
            raise ValueError('basename must be a string')
        else:
            self.basename = basename

    def get_mif(self):
        # Create mif string.
        mif = '# TimeDriver\n'
        mif += 'Specify Oxs_TimeDriver {\n'
        mif += '\tevolver {}\n'.format(self.evolver)
        mif += '\tstopping_time {}\n'.format(self.stopping_time)
        mif += '\tstage_count {}\n'.format(self.stage_count)
        mif += '\tmesh :{}\n'.format(self.mesh)
        mif += '\tMs {}\n'.format(self.Ms)
        mif += '\tm0 {\n'
        if isinstance(self.m0, (tuple, list)):
            mif += '\t\tOxs_UniformVectorField {\n'
            mif += '\t\t\tvector {'
            mif += ' {} {} {} '.format(self.m0[0], self.m0[1], self.m0[2])
            mif += '}\n'
            mif += '\t\t}\n'
        elif isinstance(self.m0, str):
            mif += '\t\tOxs_FileVectorField {\n'
            mif += '\t\t\tatlas :atlas\n'
            mif += '\t\t\tnorm 1.0\n'
            mif += '\t\t\tfile {}\n'.format(self.m0)
            mif += '\t\t}\n'
        mif += '\t}\n'
        mif += '\tbasename {}\n'.format(self.basename)
        mif += '\tvector_field_output_format {text %\#.8g}\n'
        mif += '}\n\n'

        return mif


class MinDriver(object):

    """
    class MinDriver(evolver, stopping_mxHxm, mesh, Ms, m0, basename='noname')

    The MinDriver class is used for minimisation simulations - those where the
    system is relaxed in order to find the minimum energy.

    Input
    -----
    evolver:
        String, evolver name
    stopping_mxHxm:
        The torque criteria for stopping a simulation.
    mesh:
        String, the name of the mesh.
    Ms:
        Float, int, the saturation magnetization of the system in A/m.
    m0:
        List of length 3 or string describing initial magnetization.
    basename:
        Base file name which determines the start of the name of output files.
    """

    def __init__(self, evolver, stopping_mxHxm, mesh, Ms,
                 m0, basename='noname'):
        if not isinstance(evolver, str):
            raise ValueError('evolver must be a string')
        else:
            self.evolver = evolver
        if not isinstance(stopping_mxHxm, (int, float)) or stopping_mxHxm <= 0:
            raise ValueError('stopping_mxHxm must be a positive float(int)')
        else:
            self.stopping_mxHxm = stopping_mxHxm
        if not isinstance(mesh, str):
            raise ValueError('mesh must be a string')
        else:
            self.mesh = mesh
        if not isinstance(Ms, (float, int)) or Ms <= 0:
            raise ValueError('Ms must be a positive float(int).')
        else:
            self.Ms = Ms
        if not isinstance(m0, (list, tuple, str)):
            raise ValueError('m0 must be a string, list, or tuple.')
        else:
            self.m0 = m0
        if not isinstance(basename, str):
            raise ValueError('basename must be a string')
        else:
            self.basename = basename

    def get_mif(self):
        # Create mif string.
        mif = '# MinDriver\n'
        mif += 'Specify Oxs_MinDriver {\n'
        mif += '\tevolver {}\n'.format(self.evolver)
        mif += '\tstopping_mxHxm {}\n'.format(self.stopping_mxHxm)
        mif += '\tmesh :{}\n'.format(self.mesh)
        mif += '\tMs {}\n'.format(self.Ms)
        mif += '\tm0 {\n'
        if isinstance(self.m0, (tuple, list)):
            mif += '\t\tOxs_UniformVectorField {\n'
            mif += '\t\t\tvector {'
            mif += ' {} {} {} '.format(self.m0[0], self.m0[1], self.m0[2])
            mif += '}\n'
            mif += '\t\t}\n'
        elif isinstance(self.m0, str):
            mif += '\t\tOxs_FileVectorField {\n'
            mif += '\t\t\tatlas :atlas\n'
            mif += '\t\t\tnorm 1.0\n'
            mif += '\t\t\tfile {}\n'.format(self.m0)
            mif += '\t\t}\n'
        mif += '\t}\n'
        mif += '\tbasename {}\n'.format(self.basename)
        mif += '\tvector_field_output_format {text %\#.8g}\n'
        mif += '}\n\n'

        return mif
