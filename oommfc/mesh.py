import oommfc.util as ou
import discretisedfield as df


class Mesh(df.Mesh):
    @property
    def _script(self):
        mif = ''
        if self.regions:
            # The mesh is composed of regions. Multiple BoxAtlas
            # scripts are created and the main MultiAtlas.
            for name, region in self.regions.items():
                mif += ou.mif_box_atlas(region.pmin, region.pmax, name=name)
            mif += '# MultiAtlas\n'
            mif += 'Specify Oxs_MultiAtlas:main_atlas {\n'
            for name in self.regions.keys():
                mif += f'  atlas :{name}_atlas\n'
            mif += f'  xrange {{{self.pmin[0]} {self.pmax[0]}}}\n'
            mif += f'  yrange {{{self.pmin[1]} {self.pmax[1]}}}\n'
            mif += f'  zrange {{{self.pmin[2]} {self.pmax[2]}}}\n'
            mif += '}\n\n'
        else:
            # There are no regions in the mesh.
            mif += ou.mif_box_atlas(self.pmin, self.pmax, name='main')

        if self.pbc:
            mif += '# PeriodicRectangularMesh\n'
            mif += 'Specify Oxs_PeriodicRectangularMesh:mesh {\n'
            mif += '  cellsize {{{} {} {}}}\n'.format(*self.cell)
            mif += '  atlas :main_atlas\n'
            mif += '  periodic {}\n'.format(''.join(sorted(self.pbc)))
            mif += '}\n\n'
        else:
            mif += '# RectangularMesh\n'
            mif += 'Specify Oxs_RectangularMesh:mesh {\n'
            mif += '  cellsize {{{} {} {}}}\n'.format(*self.cell)
            mif += '  atlas :main_atlas\n'
            mif += '}\n\n'

        return mif
