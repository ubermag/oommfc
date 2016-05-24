class BoxAtlas(object):
    def __init__(self, cmin, cmax, name='atlas',
                 regionname='regionname'):
        if cmin[0] >= cmax[0] or cmin[1] >= cmax[1] or cmin[2] >= cmax[2]:
            raise ValueError('Values in cmin should be smaller tha cmax.')
        else:
            self.cmin = cmin
            self.cmax = cmax

        if not isinstance(name, str):
            raise ValueError('name must be a string.')
        else:
            self.name = name

        if not isinstance(regionname, str):
            raise ValueError('regionname must be a string.')
        else:
            self.regionname = regionname

    def get_mif(self):
        # Create mif string.
        mif = '# BoxAtlas\n'
        mif += 'Specify Oxs_BoxAtlas:{}'.format(self.name) + ' {\n'
        mif += '\txrange {'
        mif += ' {} {} '.format(self.cmin[0], self.cmax[0])
        mif += '}\n'
        mif += '\tyrange {'
        mif += ' {} {} '.format(self.cmin[1], self.cmax[1])
        mif += '}\n'
        mif += '\tzrange {'
        mif += ' {} {} '.format(self.cmin[2], self.cmax[2])
        mif += '}\n'
        mif += '\tname {}\n'.format(self.regionname)
        mif += '}\n\n'

        return mif
