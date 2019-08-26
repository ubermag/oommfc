import micromagneticmodel as mm


class ZhangLi(mm.ZhangLi):
    """Zhang-Li spin-transfer torque dynamics term.

    This dynamics term models the Zhang-Li spin-transfer-torque term
    in the Landau-Lifshitz-Gilbert equation. It is defined by the
    velocity in the x-direction `u` and the non-adiabatic constant
    `beta`.

    .. math::

           \\frac{\\text{d}\\mathbf{m}}{\\text{d}t} = -(\\mathbf{u}
           \\cdot \\boldsymbol\\nabla)\\mathbf{m} + \\beta\\mathbf{m}
           \\times \\big[(\\mathbf{u} \\cdot
           \\boldsymbol\\nabla)\\mathbf{m}\\big]

    `u` can be either contant in space or spatially varying, whereas
    `beta` can be only constant in space. If `u` is constant, a single
    value is passed, e.g. `u = 0.1`. On the other hand, if it varies
    in space, there are two ways how that can be defined. The first
    one is using a dictionary, where the keys must be the same as the
    names of regions used when the mesh was defined
    (`discretisedfield.Mesh.regions`) and the values are single scalar
    values. For instance, `u = {'region1': 0.1, 'region2': 0.2}.
    Another way of defining a spatially varying parameter is by
    passing a `discretisedfield.Field` object. The field must be
    defined on the same mesh as the micromagnetic system and it must
    have an appropriate dimension `dim=1`.

    Parameters
    ----------
    u : number.Real, dict, discretisedfield.Field
      Velocity in the x-direction.
    beta : numbers.Real
      Non-adiabatic factor
    name: str (optional)
      Name of the dynamics term object. Defaults to `'zhangli'`

    Examples
    --------
    1. Defining spatially constant Zhang-Li term.

    >>> import oommfc as oc
    ...
    >>> u = 0.1
    >>> beta = 0.5
    >>> zl = oc.ZhangLi(u=u, beta=beta)
    >>> zl.u
    0.1

    2. Defining spatially varying velocity using a dictionary.

    >>> import oommfc as oc
    >>> import discretisedfield as df
    ...
    >>> p1 = (0, 0, 0)
    >>> p2 = (5e-9, 5e-9, 8e-9)
    >>> n = (5, 5, 8)
    >>> regions = {'region1': df.Region(p1=(0, 0, 0),
    ...                                 p2=(5e-9, 5e-9, 4e-9)),
    ...            'region1': df.Region(p1=(0, 0, 4e-9),
    ...                                 p2=(5e-9, 5e-9, 8e-9))}
    >>> mesh = oc.Mesh(p1=p1, p2=p2, n=n, regions=regions)
    ...
    >>> u = {'region1': 0.1, 'region2': 0.01}
    >>> beta = 0.5
    >>> zl = oc.ZhangLi(u=u, beta=beta)

    3. Defining spatially varying velocity using a
    `discretisedfield.Field` object.

    >>> import oommfc as oc
    >>> import discretisedfield as df
    ...
    >>> p1 = (0, 0, 0)
    >>> p2 = (5e-9, 5e-9, 8e-9)
    >>> n = (5, 5, 8)
    >>> mesh = oc.Mesh(p1=p1, p2=p2, n=n)
    >>> def u_value(pos):
    ...     x, y, z = pos
    ...     if z <= 4e-9:
    ...         return 0.1
    ...     else:
    ...         return 0.2
    ...
    >>> u = df.Field(mesh, dim=3, value=u_value)
    >>> zl = oc.ZhangLi(u=u, beta=beta)

    """
    pass
