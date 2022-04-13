import micromagneticmodel as mm


class SpinXferEvolver(mm.Evolver):
    """Slonczewski evolver.

    Only attributes in ``_allowed_attributes`` can be defined. For details on
    possible values for individual attributes and their default values, please
    refer to ``Oxs_SpinXferEvolve`` documentation
    (https://math.nist.gov/oommf/).

    Examples
    --------
    1. Defining evolver with a keyword argument.

    >>> import oommfc as oc
    ...
    >>> evolver = oc.SpinXferEvolver(method='rk4')

    2. Passing an argument which is not allowed.

    >>> import oommfc as oc
    ...
    >>> evolver = oc.SpinXferEvolver(myarg=3)
    Traceback (most recent call last):
       ...
    AttributeError: ...

    3. Getting the list of allowed attributes.

    >>> import oommfc as oc
    ...
    >>> evolver = oc.SpinXferEvolver()
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
        "stage_start",
        "error_rate",
        "absolute_step_error",
        "relative_step_error",
        "energy_precision",
        "min_step_headroom",
        "max_step_headroom",
        "reject_goal",
        "method",
        "P",
        "P_fixed",
        "P_free",
        "Lambda",
        "Lambda_fixed",
        "Lambda_free",
        "eps_prime",
        "J",
        "J_profile",
        "J_profile_args",
        "mp",
        "energy_slack",
    ]
