import micromagneticmodel as mm


class CGEvolver(mm.Evolver):
    """Conjugate-Gradient evolver.

    This class is used for collecting additional parameters, which
    cannot be extracted from the dynamics equation, but could be
    passed to `Oxs_CGEvolve`. Only parameters which are defined in
    `_allowed_kwargs` can be passed.

    Examples
    --------
    1. Defining evolver

    >>> import oommfc as oc
    ...
    >>> evolver = oc.CGEvolver(method='Polak-Ribiere')

    2. Passing an argument which is not allowed

    >>> import oommfc as oc
    ...
    >>> evolver = oc.CGEvolver(myarg=3)
    Traceback (most recent call last):
       ...
    AttributeError: ...

    """
    _allowed_kwargs = ['gradient_reset_angle',
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
        for kwarg in self._allowed_kwargs:
            if hasattr(self, kwarg):
                mif += f'  {kwarg} {getattr(self, kwarg)}\n'
        mif += '}\n\n'

        return mif
