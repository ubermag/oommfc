import oommfc.util as ou
import micromagneticmodel as mm


class CubicAnisotropy(mm.CubicAnisotropy):
    """Cubic anisotropy energy term.

    This energy term models cubic anisotropy term, defined by the
    anisotropy constant `K1` and the cubic anisotropy axes `u1` and
    `u2`. `u3` is then computed as a cross product of `u1` and `u2`.

    .. math::

           w_{ca} = -K_{1} [(\\mathbf{m} \\cdot
           \\mathbf{u}_{1})^{2}(\\mathbf{m} \\cdot
           \\mathbf{u}_{2})^{2} + (\\mathbf{m} \\cdot
           \\mathbf{u}_{2})^{2}(\\mathbf{m} \\cdot
           \\mathbf{u}_{3})^{2} + (\\mathbf{m} \\cdot
           \\mathbf{u}_{1})^{2}(\\mathbf{m} \\cdot
           \\mathbf{u}_{3})^{2}]

    `K1` is a scalar, given in J/m3, whereas `u1` and `u2` are
    three-dimensional vectors with real component values and no
    units. The axis directions must be non-zero at each point in the
    mesh, and will be normalized to unit magnitude before being used.

    Both the scalar parameter `K1` and the vector parameters `u1` and
    `u2` can be either contant is space or spatially varying. If they
    are constant, a single value is passed, e.g. `K1 = 1e5`, `u1 = (0,
    0, 1)`, and `u2 = (0, 1, 0)`. On the other hand, if one of them
    varies in space, there are two ways how they can be defined. The
    first one is using dictionaries, where the keys must be the same
    as the names of regions used when the mesh was defined
    (`discretisedfield.Mesh.regions`) and the values are single scalar
    or vector values. For instance, `K1 = {'region1': 1e5, 'region2':
    0}` and `u1 = {'region1': (0, 0, 1), 'region2': (1, 0,
    0)}`, etc. Another way of defining a spatially varying parameter is by
    passing a `discretisedfield.Field` object. The field must be
    defined on the same mesh as the micromagnetic system and it must
    have an appropriate dimension (`dim=1` for `K1` and `dim=3` for
    `u1` and `u2`).

    Parameters
    ----------
    K1 : numbers.Real, dict, discretisedfield.Field
      The cubic anisotropy constant
    u1, u2 : array_like, dict, discretisedfield.Field
      The cubic anisotropy axis
    name: str (optional)
      Name of the energy term object. Defaults to `'cubicanisotropy'`

    Examples
    --------
    1. Defining spatially constant cubic anisotropy

    >>> import oommfc as oc
    ...
    >>> K1 = 1e5
    >>> u1 = (0, 0, 1)
    >>> u2 = (0, 1, 0)
    >>> ca = oc.CubicAnisotropy(K1=K1, u1=u1, u2=u2)

    2. Defining spatially varying cubic anisotropy using dictionary

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
    >>> u1 = (0, 0, 1)
    >>> u2 = (0, 1, 0)
    >>> ca = oc.CubicAnisotropy(K1=K1, u1=u1, u2=u2)

    3. Defining spatially varying cubic anisotropy using a
    `discretisedfield.Field` object.

    >>> import oommfc as oc
    >>> import discretisedfield as df
    ...
    >>> p1 = (0, 0, 0)
    >>> p2 = (5e-9, 5e-9, 8e-9)
    >>> n = (5, 5, 8)
    >>> mesh = oc.Mesh(p1=p1, p2=p2, n=n)
    >>> def u1_value(pos):
    ...     x, y, z = pos
    ...     if z <= 4e-9:
    ...         return (1, 0, 0)
    ...     else:
    ...         return (0, 0, 1)
    ...
    >>> def u2_value(pos):
    ...     x, y, z = pos
    ...     if z <= 4e-9:
    ...         return (0, 1, 0)
    ...     else:
    ...         return (1, 0, 0)
    ...
    >>> K1 = 1e5
    >>> u1 = df.Field(mesh, dim=3, value=u1_value)
    >>> u2 = df.Field(mesh, dim=3, value=u2_value)
    >>> ca = oc.CubicAnisotropy(K1=K1, u1=u1, u2=u2)

    """
    @property
    def _script(self):
        k1mif, k1name = ou.setup_scalar_parameter(self.K1, 'ca_K1')
        u1mif, u1name = ou.setup_vector_parameter(self.u1, 'ca_u1')
        u2mif, u2name = ou.setup_vector_parameter(self.u2, 'ca_u2')

        mif = ''
        mif += k1mif
        mif += u1mif
        mif += u2mif
        mif += '# CubicAnisotropy\n'
        mif += 'Specify Oxs_CubicAnisotropy {\n'
        mif += f'  K1 {k1name}\n'
        mif += f'  axis1 {u1name}\n'
        mif += f'  axis2 {u2name}\n'
        mif += '}\n\n'

        return mif
