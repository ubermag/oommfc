import micromagneticmodel as mm


class EulerEvolver(mm.Evolver):
    """Euler evolver.

    This class is used for collecting additional parameters, which
    cannot be extracted from the dynamics equation, but could be
    passed to `Oxs_EulerEvolve`. Only parameters which are defined in
    `_allowed_kwargs` can be passed.

    Examples
    --------
    1. Defining evolver

    >>> import oommfc as oc
    ...
    >>> evolver = oc.EulerEvolver(start_dm=0.02)

    2. Passing an argument which is not allowed

    >>> import oommfc as oc
    ...
    >>> evolver = oc.EulerEvolver(myarg=3)
    Traceback (most recent call last):
       ...
    AttributeError: ...

    """
    _allowed_kwargs = ['alpha',
                       'gamma_LL',
                       'gamma_G',
                       'do_precess',
                       'min_timestep',
                       'max_timestep',
                       'start_dm',
                       'error_rate',
                       'absolute_step_error',
                       'relative_step_error',
                       'step_headroom']

    @property
    def _script(self):
        mif = '# EulerEvolver\n'
        mif += 'Specify Oxs_EulerEvolve:evolver {\n'
        for kwarg in self._allowed_kwargs:
            if hasattr(self, kwarg):
                mif += f'  {kwarg} {getattr(self, kwarg)}\n'
        mif += '}\n\n'

        return mif
