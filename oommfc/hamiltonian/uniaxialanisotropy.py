import oommfc.util as ou
import micromagneticmodel as mm


class UniaxialAnisotropy(mm.UniaxialAnisotropy):
    """Uniaxial anisotropy energy term.

    This energy term models uniaxial anisotropy term, defined by the
    anisotropy constant `K1` and the uniaxial anisotropy axis
    `u`.

    .. math::

           w_{ua} = -K_{1}(\\mathbf{m} \\cdot \\mathbf{u})^{2}

    `K1` is a scalar, given in J/m3, whereas `u` is a three-dimensional
    vector with real component values and no units. The axis direction
    must be non-zero at each point in the mesh, and will be normalized
    to unit magnitude before being used.

    Both the scalar parameter `K1` and the vector parameter `u` can be
    either contant is space or spatially varying. If they are
    constant, a single value is passed, e.g. `K1 = 1e5` and `u = (0,
    0, 1)`. On the other hand, if one of them varies in space, there
    are two ways how they can be defined. The first one is using
    dictionaries, where the keys must be the same as the names of
    regions used when the mesh was defined
    (`discretisedfield.Mesh.regions`) and the values are single scalar
    or vector values. For instance, `K1 = {'region1': 1e5, 'region2':
    0}` and `u = {'region1': (0, 0, 1), 'region2': (1, 0,
    0)}`. Another way of defining a spatially varying parameter is by
    passing a `discretisedfield.Field` object. The field must be
    defined on the same mesh as the micromagnetic system and it must
    have an appropriate dimension (`dim=1` for `K1` and `dim=3` for
    `u`).

    Parameters
    ----------
    K1 : numbers.Real, dict, discretisedfield.Field
      The uniaxial anisotropy constant
    u : array_like, dict, discretisedfield.Field
      The uniaxial anisotropy axis
    name: str (optional)
      Name of the energy term object. Defaults to `'uniaxialanisotropy'`

    Examples
    --------
    1. Defining spatially constant uniaxial anisotropy

    >>> import oommfc as oc
    ...
    >>> K1 = 1e5
    >>> u = (0, 0, 1)
    >>> ua = oc.UniaxialAnisotropy(K1=K1, u=u)

    2. Defining spatially varying uniaxial anisotropy using a
    dictionary

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
    >>> K1 = {'region1': 1e5, 'region2': 1e3}
    >>> u = (0, 0, 1)
    >>> ua = oc.UniaxialAnisotropy(K1=K1, u=u)

    3. Defining spatially varying uniaxial anisotropy using a
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
    ...         return (1, 0, 0)
    ...     else:
    ...         return (0, 0, 1)
    ...
    >>> K1 = 1e5
    >>> u = df.Field(mesh, dim=3, value=u_value)
    >>> ua = oc.UniaxialAnisotropy(K1=K1, u=u)

    """
    @property
    def _script(self):
        k1mif, k1name = ou.setup_scalar_parameter(self.K1, 'ua_K1')
        umif, uname = ou.setup_vector_parameter(self.u, 'ua_u')

        mif = ''
        mif += k1mif
        mif += umif
        mif += '# UniaxialAnisotropy\n'
        mif += 'Specify Oxs_UniaxialAnisotropy {\n'
        mif += f'  K1 {k1name}\n'
        mif += f'  axis {uname}\n'
        mif += '}\n\n'

        return mif
