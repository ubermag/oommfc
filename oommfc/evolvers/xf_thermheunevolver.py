import micromagneticmodel as mm


class Xf_ThermHeunEvolver(mm.Evolver):
    """Xf_ThermHeun evolver (combines Runge-Kutta and UHH_ThetaEvolve).

    Only attributes in ``_allowed_attributes`` can be defined. For details on
    possible values for individual attributes and their default values, please
    refer to ``Xf_ThermHeunEvolver`` documentation
    (https://kelvinxyfong.wordpress.com/research/research-interests/oommf-extensions/xf_thermheunevolve/).

    Examples
    --------
    1. Defining evolver with a keyword argument.

    >>> import oommfc as oc
    ...
    >>> evolver = oc.Xf_ThermHeunEvolver(method='rk4')

    2. Passing an argument which is not allowed.

    >>> import oommfc as oc
    ...
    >>> evolver = oc.Xf_ThermHeunEvolver(myarg=3)
    Traceback (most recent call last):
       ...
    AttributeError: ...

    3. Getting the list of allowed attributes.

    >>> import oommfc as oc
    ...
    >>> evolver = oc.Xf_ThermHeunEvolver()
    >>> evolver._allowed_attributes
    [...]

    """
    _allowed_attributes = ['alpha',
                           'gamma_LL',
                           'gamma_G',
                           'do_precess',
                           'allow_signed_gamma',
                           'min_timestep',
                           'max_timestep',
                           'fixed_spins',
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
                           'method',
                           'temperature',
                           'tempscript',
                           'tempscript_args',
                           'uniform_seed']
