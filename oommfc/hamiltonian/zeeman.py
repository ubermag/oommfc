import micromagneticmodel as mm


class Zeeman(mm.Zeeman):
    @property
    def script(self):
        mif = '# FixedZeeman\n'
        mif += 'Specify Oxs_FixedZeeman:{} {{\n'.format(self.name)
        mif += '  field {\n'
        mif += '    Oxs_UniformVectorField {\n'
        mif += '      vector {{{} {} {}}}\n'.format(*self.H)
        mif += '    }\n'
        mif += '  }\n'
        mif += '  multiplier 1\n'
        mif += '}\n\n'

        return mif
