class UniaxialAnisotropy(object):
    def __init__(self, K1, axis):
        if not isinstance(K1, (float, int)):
            raise ValueError('Anisotropy constant must be positive float/int.')
        else:
            self.K1 = K1
        if not isinstance(axis, (tuple, list)):
            raise ValueError('Anisotropy axis must be a tuple or list.')
        else:
            self.axis = axis

    def get_mif(self):
        # Create mif string.
        mif = '# UniaxialAnisotropy\n'
        mif += 'Specify Oxs_UniaxialAnisotropy {\n'
        mif += '\tK1 {}\n'.format(self.K1)
        mif += '\taxis {'
        mif += ' {} {} {} '.format(self.axis[0], self.axis[1], self.axis[2])
        mif += '}\n'
        mif += '}\n\n'

        return mif
