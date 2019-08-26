import micromagneticmodel as mm


class Precession(mm.Precession):
    """Precession dynamics term.

    This dynamics term models the precession in the
    Landau-Lifshitz-Gilbert equation. It is defined by the
    gyromagnetic ratio `gamma`. `gamma` is a scalar value with m/As
    units.

    .. math::

           \\frac{\\text{d}\\mathbf{m}}{\\text{d}t} = -\\gamma
           \\mathbf{m} \\times \\mathbf{H}_\\text{eff}

    `gamma` can be either contant in space or spatially varying. If it
    is constant, a single value is passed, e.g. `gamma = 2.211e5`. On
    the other hand, if it varies in space, there are two ways how that
    can be defined. The first one is using a dictionary, where the
    keys must be the same as the names of regions used when the mesh
    was defined (`discretisedfield.Mesh.regions`) and the values are
    single scalar values. For instance, `gamma = {'region1': 2.211e5,
    'region2': 0}.  Another way of defining a spatially varying
    parameter is by passing a `discretisedfield.Field` object. The
    field must be defined on the same mesh as the micromagnetic system
    and it must have an appropriate dimension `dim=1`.

    Parameters
    ----------
    gamma : number.Real, dict, discretisedfield.Field
      Gyromagetic ratio
    name: str (optional)
      Name of the dynamics term object. Defaults to `'precession'`

    Examples
    --------
    1. Defining spatially constant gyromagnetic ratio.

    >>> import oommfc as oc
    ...
    >>> gamma = oc.consts.gamma0
    >>> pr = oc.Precession(gamma=gamma)
    >>> pr.gamma
    221276.14...

    2. Defining spatially varying gyromagnetic ratio using a
    dictionary.

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
    >>> gamma = {'region1': oc.consts.gamma0, 'region2': 0}
    >>> pr = oc.Precession(gamma=gamma)

    3. Defining spatially varying gyromagnetic ratio using a
    `discretisedfield.Field` object.

    >>> import oommfc as oc
    >>> import discretisedfield as df
    ...
    >>> p1 = (0, 0, 0)
    >>> p2 = (5e-9, 5e-9, 8e-9)
    >>> n = (5, 5, 8)
    >>> mesh = oc.Mesh(p1=p1, p2=p2, n=n)
    >>> def gamma_value(pos):
    ...     x, y, z = pos
    ...     if z <= 4e-9:
    ...         return 0
    ...     else:
    ...         return 2.211e5
    ...
    >>> gamma = df.Field(mesh, dim=3, value=gamma_value)
    >>> pr = oc.Precession(gamma=gamma)

    """
    pass
