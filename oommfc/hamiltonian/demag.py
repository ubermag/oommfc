import micromagneticmodel as mm


class Demag(mm.Demag):
    """Demagnetisation energy term.

    This object models micromagnetic demagnetisation energy term. It
    does not take any mandatory arguments. However,
    `asymptotic_radius` and `name` can be passed.

    Parameters
    ----------
    asymptotic_radius : number.Real
      The asymptotic radius
    name: str (optional)
      Name of the energy term object. Defaults to `'demag'`

    Examples
    --------
    1. Initialising the demagnetisation energy term.

    >>> import oommfc as oc
    ...
    >>> demag = oc.Demag()

    """
    @property
    def _script(self):
        mif = '# Demag\n'
        mif += 'Specify Oxs_Demag {\n'
        if hasattr(self, 'asymptotic_radius'):
            mif += f'  asymptotic_radius {self.asymptotic_radius}\n'
        mif += '}\n\n'

        return mif
