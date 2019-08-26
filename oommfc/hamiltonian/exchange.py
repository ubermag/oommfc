import numbers
import oommfc.util as ou
import discretisedfield as df
import micromagneticmodel as mm


class Exchange(mm.Exchange):
    """Exchange energy term.

    This energy term models ferromagnetic exchange energy term,
    defined by the exchange energy constant `A`.

    .. math::

           w_{ex} = A(\\nabla\\mathbf{m})^{2}

    `A` is a scalar value with J/m units.

    `A` can be either contant in space or spatially varying. If it is
    constant, a single value is passed, e.g. `A = 1e-12`. On the other
    hand, if it varies in space, there are two ways how that can be
    defined. The first one is using a dictionary, where the keys must
    be the same as the names of regions used when the mesh was defined
    (`discretisedfield.Mesh.regions`) and the values are single scalar
    values. In addition, because the exhange energy constant is
    defined between discretisation cells, `A` value must be defined
    between regions as well. For example, to define `A` between
    regions, region names in the dictionary key are separated with
    `':'`. For instance, `A = {'region1': 1e-12, 'region2': 0,
    'region1:region2': 0.5e-12}`. Another way of defining a spatially
    varying parameter is by passing a `discretisedfield.Field`
    object. In this case a single value is associated to every cell
    and the exchange constant between two cells is defined as their
    average. The field must be defined on the same mesh as the
    micromagnetic system and it must have an appropriate dimension
    `dim=1`.

    Parameters
    ----------
    A : number.Real, dict, discretisedfield.Field
      The exchange energy constant
    name: str (optional)
      Name of the energy term object. Defaults to `'exchange'`

    Examples
    --------
    1. Defining spatially constant exchange energy term.

    >>> import oommfc as oc
    ...
    >>> A = 1e-12
    >>> ex = oc.Exchange(A=A)

    2. Defining spatially varying exchange energy consant using a
    dictionary.

    >>> import oommfc as oc
    >>> import discretisedfield as df
    ...
    >>> p1 = (0, 0, 0)
    >>> p2 = (5e-9, 5e-9, 8e-9)
    >>> n = (5, 5, 8)
    >>> regions = {'region1': df.Region(p1=(0, 0, 0),
    ...                                     p2=(5e-9, 5e-9, 4e-9)),
    ...            'region1': df.Region(p1=(0, 0, 4e-9),
    ...                                 p2=(5e-9, 5e-9, 8e-9))}
    >>> mesh = oc.Mesh(p1=p1, p2=p2, n=n, regions=regions)
    ...
    >>> A = {'region1': 1e-12, 'region2': 0, 'region1:region2': 0.5e-12}
    >>> ex = oc.Exchange(A=A)

    3. Defining spatially varying exchange energy constant using a
    `discretisedfield.Field` object.

    >>> import oommfc as oc
    >>> import discretisedfield as df
    ...
    >>> p1 = (0, 0, 0)
    >>> p2 = (5e-9, 5e-9, 8e-9)
    >>> n = (5, 5, 8)
    >>> mesh = oc.Mesh(p1=p1, p2=p2, n=n)
    >>> def A_value(pos):
    ...     x, y, z = pos
    ...     if z <= 4e-9:
    ...         return 0
    ...     else:
    ...         return 8.78e-11
    ...
    >>> A = df.Field(mesh, dim=3, value=A_value)
    >>> ex = oc.Exchange(A=A)

    """
    @property
    def _script(self):
        if isinstance(self.A, numbers.Real):
            mif = '# UniformExchange\n'
            mif += 'Specify Oxs_UniformExchange {\n'
            mif += f'  A {self.A}\n'
            mif += '}\n\n'
        elif isinstance(self.A, dict):
            if 'default' in self.A.keys():
                default_value = self.A['default']
            else:
                default_value = 0
            mif = '# Exchange6Ngbr\n'
            mif += 'Specify Oxs_Exchange6Ngbr {\n'
            mif += f'  default_A {default_value}\n'
            mif += '  atlas :main_atlas\n'
            mif += '  A {\n'
            for key, value in self.A.items():
                if key != 'default':
                    if ':' in key:
                        region1, region2 = key.split(':')
                    else:
                        region1, region2 = key, key
                    mif += f'    {region1} {region2} {value}\n'
            mif += '  }\n'
            mif += '}\n\n'
        elif isinstance(self.A, df.Field):
            Amif, Aname = ou.setup_scalar_parameter(self.A, 'ex_A')
            mif = Amif
            mif += '# ExchangePtwise\n'
            mif += 'Specify Oxs_ExchangePtwise {\n'
            mif += f'  A {Aname}\n'
            mif += '}\n\n'

        return mif
