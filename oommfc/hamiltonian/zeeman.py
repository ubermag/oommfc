import oommfc.util as ou
import micromagneticmodel as mm


class Zeeman(mm.Zeeman):
    """Zeeman energy term.

    This energy term models Zeeman energy term, defined by the
    external magnetic field `H`.

    .. math::

           w_{z} = -\\mu_{0}M_\\text{s}\\mathbf{m} \\cdot \\mathbf{H}

    `H` is a three-dimensional vector with real component values and
    A/m units.

    `H` can be either contant in space or spatially varying. If it is
    constant, a single value is passed, e.g. `H = (0, 0, 1e5)`. On the
    other hand, if it varies in space, there are two ways how that can
    be defined. The first one is using a dictionary, where the keys
    must be the same as the names of regions used when the mesh was
    defined (`discretisedfield.Mesh.regions`) and the values are
    single vector values. For instance, `H = {'region1': (0, 0, 1e5),
    'region2': (1e6, 0, 0)}`. Another way of defining a spatially
    varying parameter is by passing a `discretisedfield.Field`
    object. The field must be defined on the same mesh as the
    micromagnetic system and it must have an appropriate dimension
    `dim=3`.

    Parameters
    ----------
    H : array_like, dict, discretisedfield.Field
      The external magnetic field
    name: str (optional)
      Name of the energy term object. Defaults to `'zeeman'`

    Examples
    --------
    1. Defining spatially constant Zeeman energy term.

    >>> import oommfc as oc
    ...
    >>> H = (0, 0, 1e5)
    >>> ze = oc.Zeeman(H=H)

    2. Defining spatially varying external magnetic field.

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
    >>> H = {'region1': (1e5, 0, 0), 'region2': (0, 0, 1e5)}
    >>> ze = oc.Zeeman(H=H)

    3. Defining spatially varying external magnetic field using a
    `discretisedfield.Field` object.

    >>> import oommfc as oc
    >>> import discretisedfield as df
    ...
    >>> p1 = (0, 0, 0)
    >>> p2 = (5e-9, 5e-9, 8e-9)
    >>> n = (5, 5, 8)
    >>> mesh = oc.Mesh(p1=p1, p2=p2, n=n)
    >>> def H_value(pos):
    ...     x, y, z = pos
    ...     if z <= 4e-9:
    ...         return (1e5, 0, 0)
    ...     else:
    ...         return (0, 0, 1e5)
    ...
    >>> H = df.Field(mesh, dim=3, value=H_value)
    >>> ze = oc.Zeeman(H=H)

    """
    @property
    def _script(self):
        Hmif, Hname = ou.setup_vector_parameter(self.H, 'ze_H')

        mif = ''
        mif += Hmif
        mif += '# FixedZeeman\n'
        mif += 'Specify Oxs_FixedZeeman {\n'
        mif += f'  field {Hname}\n'
        mif += '}\n\n'

        return mif
