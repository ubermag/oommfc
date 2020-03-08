import oommfc as oc
import micromagneticmodel as mm


class RungeKuttaEvolver(mm.Evolver):
    """Runge-Kutta evolver.

    This class is used for collecting additional parameters, which
    cannot be extracted from the dynamics equation, but could be
    passed to `Oxs_RungeKuttaEvolve`. Only parameters which are
    defined in `_allowed_kwargs` can be passed.

    Examples
    --------
    1. Defining evolver

    >>> import oommfc as oc
    ...
    >>> evolver = oc.RungeKuttaEvolver(method='rkf54s')

    2. Passing an argument which is not allowed

    >>> import oommfc as oc
    ...
    >>> evolver = oc.RungeKuttaEvolver(myarg=3)
    Traceback (most recent call last):
       ...
    AttributeError: ...

    """
    _allowed_attributes = ['alpha',
                           'gamma_LL',
                           'gamma_G',
                           'do_precess',
                           'allow_signed_gamma',
                           'min_timestep',
                           'max_timestep',
                           'start_dm',
                           'start_dt',
                           'stage_start',
                           'error_rate',
                           'absolute_step_error',
                           'relative_step_error',
                           'energy_precision',
                           'min_step_headroom',
                           'max_step_headroom',
                           'reject_goal',
                           'method']
