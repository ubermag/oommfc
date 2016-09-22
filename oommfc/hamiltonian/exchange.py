from micromagneticmodel.hamiltonian import Exchange


class UniformExchange(Exchange):
    def script(self):
        mif = '# UniformExchange\n'
        mif += 'Specify Oxs_UniformExchange {\n'
        mif += '\tA {}\n'.format(self.A)
        mif += '}\n\n'

        return mif
