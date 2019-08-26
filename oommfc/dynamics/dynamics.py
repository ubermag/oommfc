import micromagneticmodel as mm


class Dynamics(mm.Dynamics):
    """Dynamics equation

    This class implements the sum of individual dynamics terms. It is
    obtained as a result of addition of two or more dynamics terms.

    Examples
    --------
    1. Adding a dynamics term to the dynamics equation.

    >>> import oommfc as oc
    ...
    >>> dynamics = oc.Dynamics()
    >>> dynamics += oc.Precession(gamma=oc.consts.gamma0)

    2. Creating the Hamiltoninan as a sum of two energy terms

    >>> import oommfc as oc
    ...
    >>> dynamics = oc.Precession(gamma=oc.consts.gamma0) + \
          oc.Damping(alpha=0.1)

    """
    pass
