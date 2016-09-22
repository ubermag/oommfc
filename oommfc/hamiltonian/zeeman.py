from micromagneticmodel.hamiltonian import Zeeman


class FixedZeeman(Zeeman):
    def script(self):
        mif = '# FixedZeeman\n'
        mif += 'Specify Oxs_FixedZeeman:{} '.format(self.name)
        mif += '{\n'
        mif += '\tfield {\n'
        mif += '\t\tOxs_UniformVectorField {\n'
        mif += '\t\t\tvector {'
        mif += ' {} {} {} '.format(self.H[0], self.H[1], self.H[2])
        mif += '}\n'
        mif += '\t\t}\n'
        mif += '\t}\n'
        mif += '\tmultiplier {}\n'.format(1)
        mif += '}\n\n'

        return mif
