import oommfc.util as ou
import micromagneticmodel as mm


class RungeKuttaEvolver(mm.Evolver):
    _allowed_kwargs = ['alpha',
                       'gamma_LL',
                       'gamma_G',
                       'do_precess',
                       'allow_signed_gamma',
                       'min_timestep',
                       'max_timestep',
                       'start_dm',
                       'start_dt',
                       'stage_start',
                       'error_rate',
                       'absolute_step_error',
                       'relative_step_error',
                       'energy_precision',
                       'min_step_headroom',
                       'max_step_headroom',
                       'reject_goal',
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

        mif += '# RungeKuttaEvolver\n'
        mif += 'Specify Oxs_RungeKuttaEvolve:evolver {\n'
        for kwarg in self._allowed_kwargs:
            if hasattr(self, kwarg):
                mif += f'  {kwarg} {getattr(self, kwarg)}\n'
        mif += '}\n\n'

        return mif
