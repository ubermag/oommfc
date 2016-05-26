
"""
evolvers.py

Evolvers describe the algorithm which is used to drive the simulation, and
update the magnetization at each step. There are two types - time evolvers
and minimization evolvers. These evolvers are controlled by drivers.


For more detail consult the OOMMF Standard Oxs_Ext Child Classes documentation.
"""


class RungeKuttaEvolve(object):

    """
    class RungeKuttaEvolve(alpha, gamma_G=2.210173e5, start_dm=0.01,
                           method='rkf54')

    Time evolver which integrates the Landau-Lifshitz-Gilbert equation
    using a specified Runge-Kutta method. By default, the rkf54 algorithm is
    used.

    Input
    -----
    alpha:
        Damping constant alpha in LLG equation
    gamma_G:
        Gilbert gyromagnetic ratio
    start_dm:
        Maximum change in the normalised magnetization (degrees).
    method:
        String, one of rk2, rk4, rkf54, rkf54m, rkf54s.
    """

    def __init__(self, alpha, gamma_G=2.210173e5,
                 start_dm=0.01, method='rkf54'):
        if not isinstance(alpha, (int, float)) or alpha < 0:
            raise ValueError('alpha must be a positive float or int.')
        else:
            self.alpha = alpha

        if not isinstance(gamma_G, (float, int)) or gamma_G <= 0:
            raise ValueError('gamma_G must be a positive float or int.')
        else:
            self.gamma_G = gamma_G

        if not isinstance(start_dm, (float, int)) or start_dm <= 0:
            raise ValueError('start_dm must be a positive float or int.')
        else:
            self.start_dm = start_dm

        if not isinstance(method, str):
            raise ValueError('method must be a string')
        if method not in ['rk2', 'rk4', 'rkf54', 'rkf54m', 'rkf54s']:
            raise ValueError('method is not valid')
        else:
            self.method = method

    def get_mif(self):
        # Create mif string.
        mif = '# RungeKutta evolver\n'
        mif += 'Specify Oxs_RungeKuttaEvolve:evolver {\n'
        mif += '\talpha {}\n'.format(self.alpha)
        mif += '\tgamma_G {}\n'.format(self.gamma_G)
        mif += '\tstart_dm {}\n'.format(self.start_dm)
        mif += '\tmethod {}\n'.format(self.method)
        mif += '}\n\n'

        return mif


class CGEvolve(object):

    """
    class RungeKuttaEvolve()

    Minimisation evolver which locates local energy minima using a conjugate
    gradient method.
    """

    def __init__(self):
        pass

    def get_mif(self):
        mif = '# CG evolver\n'
        mif += 'Specify Oxs_CGEvolve:evolver {}\n\n'

        return mif
