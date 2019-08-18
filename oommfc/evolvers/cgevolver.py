import micromagneticmodel as mm


class CGEvolver(mm.Evolver):
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
