import oommfc.util as ou
import discretisedfield as df


class Mesh(df.Mesh):
    """Finite difference mesh.

    A rectangular mesh domain spans between two points
    :math:`\\mathbf{p}_{1}` and :math:`\\mathbf{p}_{2}`. The domain is
    discretised using a finite difference cell, whose dimensions are
    defined with `cell`. Alternatively, the domain can be discretised
    by passing the number of discretisation cells `n` in all three
    dimensions. Either `cell` or `n` should be defined to discretise
    the domain, not both. Periodic boundary conditions can be
    specified by passing `pbc` argument, which is an iterable
    containing one or more elements from ``['x', 'y', 'z']``. The
    parameter `name` is optional and defaults to 'mesh'.

    In order to properly define a mesh, the length of all mesh domain
    edges must not be zero and the mesh domain must be an aggregate of
    discretisation cells.

    Parameters
    ----------
    p1, p2 : (3,) array_like
        Points between which the mesh domain spans :math:`\\mathbf{p}
        = (p_{x}, p_{y}, p_{z})`.
    cell : (3,) array_like, optional
        Discretisation cell size :math:`(d_{x}, d_{y}, d_{z})`. Either
        `cell` or `n` should be defined, not both.
    n : (3,) array_like, optional
        The number of discretisation cells :math:`(n_{x}, n_{y},
        n_{z})`. Either `cell` or `n` should be defined, not both.
    pbc : iterable, optional
        Periodic boundary conditions in x, y, or z direction. Its value
        is an iterable consisting of one or more characters `x`, `y`,
        or `z`, denoting the direction(s) in which the mesh is periodic.
    regions : dict, optional
        A dictionary defining regions inside the mesh. The keys of the
        dictionary are the region names (str), whereas the values are
        `discretisedfield.Region` objects.
    name : str, optional
        Mesh name (the default is 'mesh'). The mesh name must be a valid
        Python variable name string. More specifically, it must not
        contain spaces, or start with underscore or numeric character.

    Raises
    ------
    ValueError
        If the length of one or more mesh domain edges is zero, or
        mesh domain is not an aggregate of discretisation cells.

    Examples
    --------
    1. Defining a nano-sized thin film mesh by passing `cell` parameter

    >>> import oommfc as oc
    ...
    >>> p1 = (-50e-9, -25e-9, 0)
    >>> p2 = (50e-9, 25e-9, 5e-9)
    >>> cell = (1e-9, 1e-9, 0.1e-9)
    >>> name = 'mesh_name'
    >>> mesh = oc.Mesh(p1=p1, p2=p2, cell=cell, name=name)

    2. Defining a nano-sized thin film mesh by passing `n` parameter

    >>> import oommfc as oc
    ...
    >>> p1 = (-50e-9, -25e-9, 0)
    >>> p2 = (50e-9, 25e-9, 5e-9)
    >>> n = (100, 50, 5)
    >>> name = 'mesh_name'
    >>> mesh = oc.Mesh(p1=p1, p2=p2, n=n, name=name)

    3. Defining a mesh with periodic boundary conditions in x and y
    directions.

    >>> import oommfc as oc
    ...
    >>> p1 = (0, 0, 0)
    >>> p2 = (100, 100, 1)
    >>> n = (100, 100, 1)
    >>> pbc = 'xy'
    >>> mesh = oc.Mesh(p1=p1, p2=p2, n=n, pbc=pbc, name=name)

    4. Defining a mesh with two regions.

    >>> import oommfc as oc
    ...
    >>> p1 = (0, 0, 0)
    >>> p2 = (100, 100, 100)
    >>> n = (10, 10, 10)
    >>> regions = {'r1': df.Region(p1=(0, 0, 0), p2=(50, 100, 100)),
    ...            'r2': df.Region(p1=(50, 0, 0), p2=(100, 100, 100))}
    >>> mesh = oc.Mesh(p1=p1, p2=p2, n=n, regions=regions)

    5. An attempt to define a mesh with invalid parameters, so that
    the ``ValueError`` is raised. In this example, the mesh domain is
    not an aggregate of discretisation cells in the :math:`z`
    direction.

    >>> import oommfc as oc
    ...
    >>> p1 = (-25, 3, 0)
    >>> p2 = (25, 6, 1)
    >>> cell = (5, 3, 0.4)
    >>> mesh = oc.Mesh(p1=p1, p2=p2, cell=cell, name=name)
    Traceback (most recent call last):
        ...
    ValueError: ...

    """
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
