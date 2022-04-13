import micromagneticmodel as mm


class CGEvolver(mm.Evolver):
    """Conjugate-Gradient evolver.

    Only attributes in ``_allowed_attributes`` can be defined. For details on
    possible values for individual attributes and their default values, please
    refer to ``Oxs_CGEvolver`` documentation (https://math.nist.gov/oommf/).

    Examples
    --------
    1. Defining evolver with a keyword argument.

    >>> import oommfc as oc
    ...
    >>> evolver = oc.CGEvolver(method='Polak-Ribiere')

    2. Passing an argument which is not allowed.

    >>> import oommfc as oc
    ...
    >>> evolver = oc.CGEvolver(myarg=3)
    Traceback (most recent call last):
       ...
    AttributeError: ...

    3. Getting the list of allowed attributes.

    >>> import oommfc as oc
    ...
    >>> evolver = oc.CGEvolver()
    >>> evolver._allowed_attributes
    [...]

    """

    _allowed_attributes = [
        "gradient_reset_angle",
        "gradient_reset_count",
        "minimum_bracket_step",
        "maximum_bracket_step",
        "line_minimum_angle_precision",
        "line_minimum_relwidth",
        "energy_precision",
        "method",
        "fixed_spins",
    ]
