import micromagneticmodel as mm


class SpinTEvolver(mm.Evolver):
    """Zhang-Li evolver.

    Only attributes in ``_allowed_attributes`` can be defined. For details on
    possible values for individual attributes and their default values, please
    refer to ``Anv_SpinTEvolve`` documentation
    (https://www.zurich.ibm.com/st/nanomagnetism/spintevolve.html).

    Examples
    --------
    1. Defining evolver with a keyword argument.

    >>> import oommfc as oc
    ...
    >>> evolver = oc.SpinTEvolver(method='rk4')

    2. Passing an argument which is not allowed.

    >>> import oommfc as oc
    ...
    >>> evolver = oc.SpinTEvolver(myarg=3)
    Traceback (most recent call last):
       ...
    AttributeError: ...

    3. Getting the list of allowed attributes.

    >>> import oommfc as oc
    ...
    >>> evolver = oc.SpinTEvolver()
    >>> evolver._allowed_attributes
    [...]

    """
    _allowed_attributes = ['alpha',
                           'gamma_LL',
                           'gamma_G',
                           'do_precess',
                           'u',
                           'u_profile',
                           'u_profile_args',
                           'beta',
                           'method']
