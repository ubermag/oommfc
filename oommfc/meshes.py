"""
meshes.py

Meshes in OOMMF describe the space over which the simulation occurs - there
should be only a single mesh in a given simulation. A mesh is constructed over
an atlas which describes the simulation geometry.

"""
import textwrap
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

    def __init__(self, atlas, d, meshname='mesh',periodicity=(0,0,0)):
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
        if not isinstance(periodicity, tuple) or len(periodicity) != 3:
            raise ValueError('periodicity must be a length 3 tuple')
        else:
            self.periodicity = periodicity

    def get_mif(self):
        if self.periodicity == (0,0,0):
            # Create mif string.
            mif = textwrap.dedent("""\
            # RectangularMesh
            Specify Oxs_RectangularMesh:{} {{
            \tcellsize {{ {} {} {} }}
            \tatlas :{}
            }}
            """).format(self.meshname, self.d[0], self.d[1], self.d[2], self.atlas.name)
        else:
            periodicstring = []
            if self.periodicity[0] == 1:
                periodicstring.append('x')
            if self.periodicity[1] == 1:
                periodicstring.append('y')
            if self.periodicity[2] == 1:
                periodicstring.append('z')
            periodicstring = str(periodicstring)
            mif = textwrap.dedent("""\
            # RectangularMesh
            Specify Oxs_PeriodicRectangularMesh:{} {{
            cellsize {{ {} {} {} }}
            atlas {}
            periodic {}
            }}

            
            """).format(self.meshname, self.d[0], self.d[1],
                        self.d[2], self.atlas.name, periodicstring)

        return mif
