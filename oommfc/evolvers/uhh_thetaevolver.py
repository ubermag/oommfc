import micromagneticmodel as mm


class UHH_ThetaEvolver(mm.Evolver):
    """Models finite temperature via a differential equation of Langevin type.

    Only attributes in ``_allowed_attributes`` can be defined. For details on
    possible values for individual attributes and their default values, please
    refer to ``thetaevolve`` documentation
    (http://www.nanoscience.de/group_r/stm-spstm/projects/temperature/download.shtml).

    Examples
    --------
    1. Defining evolver with a keyword argument.

    >>> import oommfc as oc
    ...
    >>> evolver = oc.UHH_ThetaEvolver(fixed_timestep=2e-13, temperature=60)

    2. Passing an argument which is not allowed.

    >>> import oommfc as oc
    ...
    >>> evolver = oc.UHH_ThetaEvolver(myarg=3)
    Traceback (most recent call last):
       ...
    AttributeError: ...

    3. Getting the list of allowed attributes.

    >>> import oommfc as oc
    ...
    >>> evolver = oc.UHH_ThetaEvolver()
    >>> evolver._allowed_attributes
    [...]

    """
    _allowed_attributes = ['alpha',
                           'do_precess',
                           'gamma_LL',

                           'fixed_timestep',
                           'temperature',
                           'uniform_seed',
                           'ito_calculus']
