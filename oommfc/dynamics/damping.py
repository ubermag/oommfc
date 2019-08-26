import micromagneticmodel as mm


class Damping(mm.Damping):
    """Gilbert damping dynamics term.

    This dynamics term models the Gilbert damping in the
    Landau-Lifshitz-Gilbert equation. It is defined by the Gilbert
    damping `alpha`. `alpha` is a scalar value with no units.

    .. math::

           \\frac{\\text{d}\\mathbf{m}}{\\text{d}t} = -\\alpha
           \\left(\\mathbf{m} \\times
           \\frac{\\text{d}\\mathbf{m}}{\\text{d}t} \\right)

    `alpha` can be either contant in space or spatially varying. If it
    is constant, a single value is passed, e.g. `alpha = 0.01`. On
    the other hand, if it varies in space, there are two ways how that
    can be defined. The first one is using a dictionary, where the
    keys must be the same as the names of regions used when the mesh
    was defined (`discretisedfield.Mesh.regions`) and the values are
    single scalar values. For instance, `alpha = {'region1': 0.1,
    'region2': 1}.  Another way of defining a spatially varying
    parameter is by passing a `discretisedfield.Field` object. The
    field must be defined on the same mesh as the micromagnetic system
    and it must have an appropriate dimension `dim=1`.

    Parameters
    ----------
    alpha : number.Real, dict, discretisedfield.Field
      Gilbert damping
    name: str (optional)
      Name of the dynamics term object. Defaults to `'damping'`

    Examples
    --------
    1. Defining spatially constant Gilbert damping.

    >>> import oommfc as oc
    ...
    >>> alpha = 0.1
    >>> dp = oc.Damping(alpha=alpha)
    >>> dp.alpha
    0.1

    2. Defining spatially varying Gilbert damping using a dictionary.

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
    >>> alpha = {'region1': 0.1, 'region2': 0.01}
    >>> dp = oc.Damping(alpha=alpha)

    3. Defining spatially varying Gilbert damping using a
    `discretisedfield.Field` object.

    >>> import oommfc as oc
    >>> import discretisedfield as df
    ...
    >>> p1 = (0, 0, 0)
    >>> p2 = (5e-9, 5e-9, 8e-9)
    >>> n = (5, 5, 8)
    >>> mesh = oc.Mesh(p1=p1, p2=p2, n=n)
    >>> def alpha_value(pos):
    ...     x, y, z = pos
    ...     if z <= 4e-9:
    ...         return 0
    ...     else:
    ...         return 2.211e5
    ...
    >>> alpha = df.Field(mesh, dim=3, value=alpha_value)
    >>> dp = oc.Damping(alpha=alpha)

    """
    pass
