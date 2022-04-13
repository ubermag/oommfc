import micromagneticmodel as mm


class EulerEvolver(mm.Evolver):
    """Euler evolver.

    Only attributes in ``_allowed_attributes`` can be defined. For details on
    possible values for individual attributes and their default values, please
    refer to ``Oxs_EulerEvolver`` documentation (https://math.nist.gov/oommf/).

    Examples
    --------
    1. Defining evolver with a keyword argument.

    >>> import oommfc as oc
    ...
    >>> evolver = oc.EulerEvolver(min_timestep=0)

    2. Passing an argument which is not allowed.

    >>> import oommfc as oc
    ...
    >>> evolver = oc.EulerEvolver(myarg=3)
    Traceback (most recent call last):
       ...
    AttributeError: ...

    3. Getting the list of allowed attributes.

    >>> import oommfc as oc
    ...
    >>> evolver = oc.EulerEvolver()
    >>> evolver._allowed_attributes
    [...]

    """

    _allowed_attributes = [
        "alpha",
        "gamma_LL",
        "gamma_G",
        "do_precess",
        "min_timestep",
        "max_timestep",
        "fixed_spins",
        "start_dm",
        "error_rate",
        "absolute_step_error",
        "relative_step_error",
        "step_headroom",
    ]
