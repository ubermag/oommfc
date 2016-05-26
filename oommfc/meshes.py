"""
meshes.py

Meshes in OOMMF describe the space over which the simulation occurs - there
should be only a single mesh in a given simulation. A mesh is constructed over
an atlas which describes the simulation geometry.

"""

from .atlases import BoxAtlas


class RectangularMesh(object):

    """
    class RectangularMesh(atlas, d, meshname='mesh')

    Creates a rectangular mesh across the space covered by atlas.

    Inputs
    ------
    atlas:
        An object of type BoxAtlas.
    d:
        List of length 3, specifies cell sizes in Finite Difference scheme.
    meshname:
        String, name of the mesh in OOMMF.
    """

    def __init__(self, atlas, d, meshname='mesh'):
        if not isinstance(d, (tuple, list)) or len(d) != 3:
            raise ValueError('Cellsize d must be a tuple of length 3.')
        elif d[0] <= 0 or d[1] <= 0 or d[2] <= 0:
            raise ValueError('Cellsize dimensions must be positive.')
        else:
            self.d = d

        if not isinstance(atlas, BoxAtlas):
            raise ValueError('atlas must be a BoxAtlas object.')
        else:
            self.atlas = atlas

        if not isinstance(meshname, str):
            raise ValueError('name must be a string.')
        else:
            self.meshname = meshname

    def get_mif(self):
        # Create mif string.
        mif = '# RectangularMesh\n'
        mif += 'Specify Oxs_RectangularMesh:{}'.format(self.meshname) + ' {\n'
        mif += '\tcellsize {'
        mif += ' {} {} {} '.format(self.d[0], self.d[1], self.d[2])
        mif += '}\n'
        mif += '\tatlas {}\n'.format(self.atlas.name)
        mif += '}\n\n'

        return mif
