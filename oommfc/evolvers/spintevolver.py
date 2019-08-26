import oommfc.util as ou
import micromagneticmodel as mm


class SpinTEvolver(mm.Evolver):
    """Zhang-Li evolver.

    This class is used for collecting additional parameters, which
    cannot be extracted from the dynamics equation, but could be
    passed to `Anv_SpinTEvolve`. Only parameters which are
    defined in `_allowed_kwargs` can be passed.

    Examples
    --------
    1. Defining evolver

    >>> import oommfc as oc
    ...
    >>> evolver = oc.SpinTEvolver(method='rkf54s')

    2. Passing an argument which is not allowed

    >>> import oommfc as oc
    ...
    >>> evolver = oc.SpinTEvolver(myarg=3)
    Traceback (most recent call last):
       ...
    AttributeError: ...

    """
    _allowed_kwargs = ['alpha',
                       'gamma_LL',
                       'gamma_G',
                       'do_precess',
                       'u',
                       'beta',
                       'method']

    @property
    def _script(self):
        # Prepare spatially varying fields.
        mif = ''
        if hasattr(self, 'gamma_G'):
            gammamif, gammaname = ou.setup_scalar_parameter(self.gamma_G,
                                                            'pr_gamma')
            self.gamma_G = gammaname
            mif += gammamif
        if hasattr(self, 'alpha'):
            alphamif, alphaname = ou.setup_scalar_parameter(self.alpha,
                                                            'dp_alpha')
            self.alpha = alphaname
            mif += alphamif
        if hasattr(self, 'u'):
            umif, uname = ou.setup_scalar_parameter(self.u, 'zl_alpha')
            self.u = uname
            mif += umif

        mif += '# Zhang-Li evolver\n'
        mif += 'Specify Anv_SpinTEvolve:evolver {\n'
        for kwarg in self._allowed_kwargs:
            if hasattr(self, kwarg):
                mif += f'  {kwarg} {getattr(self, kwarg)}\n'
        mif += '}\n\n'

        return mif
