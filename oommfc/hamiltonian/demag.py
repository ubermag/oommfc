import micromagneticmodel as mm


class Demag(mm.Demag):
    @property
    def _script(self):
        mif = '# Demag\n'
        mif += 'Specify Oxs_Demag {\n'
        if hasattr(self, 'asymptotic_radius'):
            mif += f'  asymptotic_radius {self.asymptotic_radius}\n'
        mif += '}\n\n'

        return mif
