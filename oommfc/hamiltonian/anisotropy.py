from micromagneticmodel.hamiltonian import UniaxialAnisotropy


class UniaxialAnisotropy(UniaxialAnisotropy):
    def script(self):
        mif = '# UniaxialAnisotropy\n'
        mif += 'Specify Oxs_UniaxialAnisotropy {\n'
        mif += '\tK1 {}\n'.format(self.K)
        mif += '\taxis {'
        mif += ' {} {} {} '.format(self.u[0], self.u[1], self.u[2])
        mif += '}\n'
        mif += '}\n\n'

        return mif
