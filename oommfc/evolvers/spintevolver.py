import oommfc.util as ou
import micromagneticmodel as mm


class SpinTEvolver(mm.Evolver):
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
            gammamif, gammaname = ou.setup_scalar_parameter(self.gamma_G, 'pr_gamma')
            self.gamma_G = gammaname
            mif += gammamif
        if hasattr(self, 'alpha'):
            alphamif, alphaname = ou.setup_scalar_parameter(self.alpha, 'dp_alpha')
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
