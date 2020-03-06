import oommfc as oc


def mesh_script(mesh):
    """Returns calculator's script.

    Parameters
    ----------
    mesh : discretisedfield.Mesh

        Mesh object.

    Returns
    -------
    str

        Calculator's script.

    Examples
    --------
    1. Getting calculator's script.

    >>> import discretisedfield as df
    >>> import oommfc as oc
    ...
    >>> p1 = (0, 0, 0)
    >>> p2 = (10, 10, 10)
    >>> n = (5, 5, 5)
    >>> region = df.Region(p1=p1, p2=p2)
    >>> mesh = df.Mesh(region=region, n=n)
    >>> oc.script.mesh_script(mesh)
    '# BoxAtlas...'

    """
    mif = ''
    if mesh.subregions:
        # The mesh is composed of subregions. Multiple BoxAtlas scripts are
        # generated and the main MultiAtlas.
        for name, subregion in mesh.subregions.items():
            mif += oc.script.box_atlas(subregion.pmin, subregion.pmax,
                                       name=name)
        mif += '# MultiAtlas\n'
        mif += 'Specify Oxs_MultiAtlas:main_atlas {\n'
        for name in mesh.subregions.keys():
            mif += f'  atlas :{name}_atlas\n'
        mif += f'  xrange {{ {mesh.region.pmin[0]} {mesh.region.pmax[0]} }}\n'
        mif += f'  yrange {{ {mesh.region.pmin[1]} {mesh.region.pmax[1]} }}\n'
        mif += f'  zrange {{ {mesh.region.pmin[2]} {mesh.region.pmax[2]} }}\n'
        mif += '}\n\n'
    else:
        # There are no subregions in the mesh.
        mif += oc.script.box_atlas(mesh.region.pmin, mesh.region.pmax,
                                   name='main')

    if mesh.pbc:
        mif += '# PeriodicRectangularMesh\n'
        mif += 'Specify Oxs_PeriodicRectangularMesh:mesh {\n'
        mif += '  cellsize {{ {} {} {} }}\n'.format(*mesh.cell)
        mif += '  atlas :main_atlas\n'
        mif += '  periodic {}\n'.format(''.join(sorted(mesh.pbc)))
        mif += '}\n\n'
    else:
        mif += '# RectangularMesh\n'
        mif += 'Specify Oxs_RectangularMesh:mesh {\n'
        mif += '  cellsize {{ {} {} {} }}\n'.format(*mesh.cell)
        mif += '  atlas :main_atlas\n'
        mif += '}\n\n'

    return mif
