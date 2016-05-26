"""
atlases.py

Atlases are geometric regions in space which are used
to define the problem domain in OOMMF. This module contains
classes which correspond to different types of geometry.
"""


class BoxAtlas(object):

    """
    class BoxAtlas(self, cmin, cmax, name='atlas',
                   regionname='regionname'):

    This class defines a single region which is a box.

    Inputs
    ------
    cmin:
        List of 3 coordinates representing bottom corner of box.
    cmax:
        List of 3 coordinates representing opposite upper corner of box.
    name:
        String, label assigned to the region in the atlas.

    Example
    -------

    To create a 50nm x 50nm x 50nm box:

    atlas = BoxAtlas([0, 0, 0], [50, 50, 50])
    """

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
        """
        Returns MIF string.
        """
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
