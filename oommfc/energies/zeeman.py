import numpy as np


class FixedZeeman(object):
    def __init__(self, H, multiplier=1, name='fixedzeeman'):
        if not isinstance(H, (list, tuple, np.ndarray)) or len(H) != 3:
            raise ValueError('H must be a 3-element tuple or list.')
        else:
            self.H = H

        if not isinstance(multiplier, (float, int)):
            raise ValueError('Multiplier must be a positive float or int.')
        else:
            self.multiplier = multiplier

        if not isinstance(name, str):
            raise ValueError('name must be a string.')
        else:
            self.name = name

    def get_mif(self):
        # Create mif string.
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
        mif += '\tmultiplier {}\n'.format(self.multiplier)
        mif += '}\n\n'

        return mif
