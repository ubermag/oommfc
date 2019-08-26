import sys
import numbers
import micromagneticmodel as mm


class DMI(mm.DMI):
    """Dzyaloshinskii-Moriya energy term.

    This energy term models DM energy term, defined by the DM energy
    constant `D` and crystalographic class `crystalclass`. `D` is a
    scalar value with J/m2 units.

    .. math::

           \\mathbf{w_\\text{dmi}} = \\left\\{
           \\begin{array}{ll}
           D \\mathbf{m} \\cdot (\\nabla \\times \\mathbf{m}), &
           \\text{for}\\,\\,T(O) \\\\ D ( \\mathbf{m} \\cdot \\nabla m_{z} -
           m_{z} \\nabla \\cdot \\mathbf{m}), & \\text{for}\\,\\,C_{nv} \\\\
           D\\mathbf{m} \\cdot \\left( \\frac{\\partial
           \\mathbf{m}}{\\partial x} \\times \\hat{x} - \\frac{\\partial
           \\mathbf{m}}{\partial y} \\times \\hat{y} \\right), &
           \\text{for}\\,\\,D_{2d} \\\\
           \\end{array} \\right.

    `D` can be either contant in space or spatially varying. If it is
    constant, a single value is passed, e.g. `D = 1e-3`. On the other
    hand, if it varies in space, there is only one way how that can be
    defined: using a dictionary. The keys must be the same as the
    names of regions used when the mesh was defined
    (`discretisedfield.Mesh.regions`) and the values are single scalar
    values. In addition, because the DM energy constant is defined
    between discretisation cells, `D` value must be defined between
    regions as well. For example, to define `D` between regions,
    region names in the dictionary key are separated with `':'`. For
    instance, `D = {'region1': 1e-3, 'region2': 0, 'region1:region2':
    0.5e-3}`. This term cannot be set using `discretisedfield.Field`
    object.

    Parameters
    ----------
    D : number.Real, dict
      The Dzyaloshinskii-Moriya energy constant
    name: str (optional)
      Name of the energy term object. Defaults to `'dmi'`

    Examples
    --------
    1. Defining spatially constant DM energy term.

    >>> import oommfc as oc
    ...
    >>> D = 1e-3
    >>> dmi = oc.DMI(D=D, crystalclass='Cnv')

    2. Defining spatially varying DM energy consant using a
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
    >>> D = {'region1': 1e-3, 'region2': 0, 'region1:region2': 0.5e-3}
    >>> dmi = oc.DMI(D=D, crystalclass='D2d')

    """
    @property
    def _script(self):
        if self.crystalclass in ['t', 'o'] and sys.platform != 'win32':
            oxs = 'Oxs_DMI_T'
        elif self.crystalclass == 'd2d' and sys.platform != 'win32':
            oxs = 'Oxs_DMI_D2d'
        elif self.crystalclass == 'cnv' and sys.platform != 'win32':
            oxs = 'Oxs_DMI_Cnv'
        elif self.crystalclass == 'cnv' and sys.platform == 'win32':
            oxs = 'Oxs_DMExchange6Ngbr'
        else:
            raise ValueError(f'The {self.crystalclass} crystal class is not '
                             f'supported on {sys.platform} platform.')

        mif = f'# DMI of crystallographic class {self.crystalclass}\n'
        mif += f'Specify {oxs} {{\n'
        if isinstance(self.D, numbers.Real):
            mif += f'  default_D {self.D}\n'
            mif += '  atlas :main_atlas\n'
            mif += '  D {\n'
            mif += f'    main main {self.D}\n'
            mif += '  }\n'
            mif += '}\n\n'
        elif isinstance(self.D, dict):
            if 'default' in self.D.keys():
                default_value = self.D['default']
            else:
                default_value = 0
            mif += f'  default_D {default_value}\n'
            mif += '  atlas :main_atlas\n'
            mif += '  D {\n'
            for key, value in self.D.items():
                if key != 'default':
                    if ':' in key:
                        region1, region2 = key.split(':')
                    else:
                        region1, region2 = key, key
                    mif += f'    {region1} {region2} {value}\n'
            mif += '  }\n'
            mif += '}\n\n'
        else:
            msg = f'Type {type(self.D)} not supported.'
            raise ValueError(msg)

        return mif
