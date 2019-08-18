import micromagneticmodel as mm


class EulerEvolver(mm.Evolver):
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
