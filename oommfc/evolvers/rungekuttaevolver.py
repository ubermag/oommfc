import micromagneticmodel as mm


class RungeKuttaEvolver(mm.Evolver):
    """Runge-Kutta evolver.

    Only attributes in ``_allowed_attributes`` can be defined. For details on
    possible values for individual attributes and their default values, please
    refer to ``Oxs_RungeKuttaEvolver`` documentation
    (https://math.nist.gov/oommf/).

    Examples
    --------
    1. Defining evolver with a keyword argument.

    >>> import oommfc as oc
    ...
    >>> evolver = oc.RungeKuttaEvolver(method='rk4')

    2. Passing an argument which is not allowed.

    >>> import oommfc as oc
    ...
    >>> evolver = oc.RungeKuttaEvolver(myarg=3)
    Traceback (most recent call last):
       ...
    AttributeError: ...

    3. Getting the list of allowed attributes.

    >>> import oommfc as oc
    ...
    >>> evolver = oc.RungeKuttaEvolver()
    >>> evolver._allowed_attributes
    [...]

    """

    _allowed_attributes = [
        "alpha",
        "gamma_LL",
        "gamma_G",
        "do_precess",
        "allow_signed_gamma",
        "min_timestep",
        "max_timestep",
        "fixed_spins",
        "start_dm",
        "start_dt",
        "stage_start",
        "error_rate",
        "absolute_step_error",
        "relative_step_error",
        "energy_precision",
        "min_step_headroom",
        "max_step_headroom",
        "reject_goal",
        "method",
    ]
