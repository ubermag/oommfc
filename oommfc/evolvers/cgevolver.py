import micromagneticmodel as mm


class CGEvolver(mm.Evolver):
    """Conjugate-Gradient evolver.

    Only parameters which are defined in ``_allowed_attributes`` can be passed.

    Examples
    --------
    1. Defining evolver with a keyword argument.

    >>> import oommfc as oc
    ...
    >>> evolver = oc.CGEvolver(method='Polak-Ribiere')

    2. Passing an argument which is not allowed.

    >>> import oommfc as oc
    ...
    >>> evolver = oc.CGEvolver(myarg=3)
    Traceback (most recent call last):
       ...
    AttributeError: ...

    """
    _allowed_attributes = ['gradient_reset_angle',
                           'gradient_reset_count',
                           'minimum_bracket_step',
                           'maximum_bracket_step',
                           'line_minimum_angle_precision',
                           'line_minimum_relwidth',
                           'energy_precision',
                           'method']

    @property
    def _script(self):
        mif = '# CGEvolver\n'
        mif += 'Specify Oxs_CGEvolve:evolver {\n'
        for attr in self._allowed_attributes:
            if hasattr(self, attr):
                mif += f'  {attr} {getattr(self, attr)}\n'
        mif += '}\n\n'

        return mif
