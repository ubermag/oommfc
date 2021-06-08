import micromagneticmodel as mm

class UHH_ThetaEvolver(mm.Evolver):
    """Theta evolver.

    """
    _allowed_attributes = ['alpha',
                           'do_precess',
                           'gamma_LL',

                           'fixed_timestep',
                           'temperature',
                           'uniform_seed',
                           'ito_calculus']
