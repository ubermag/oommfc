import oommfc as oc


def mesh_script(mesh):
    mif = ""
    # Define atlas.
    if mesh.subregions:
        # The mesh is composed of subregions. Multiple BoxAtlas scripts are
        # generated and the main MultiAtlas.
        for name, subregion in mesh.subregions.items():
            mif += oc.scripts.box_atlas(subregion.pmin, subregion.pmax, name=name)
        mif += oc.scripts.box_atlas(mesh.region.pmin, mesh.region.pmax, name="entire")
        mif += "# MultiAtlas\n"
        mif += "Specify Oxs_MultiAtlas:main_atlas {\n"
        for name in mesh.subregions.keys():
            mif += f"  atlas :{name}_atlas\n"
        mif += "  atlas :entire_atlas\n"
        mif += f"  xrange {{ {mesh.region.pmin[0]} {mesh.region.pmax[0]} }}\n"
        mif += f"  yrange {{ {mesh.region.pmin[1]} {mesh.region.pmax[1]} }}\n"
        mif += f"  zrange {{ {mesh.region.pmin[2]} {mesh.region.pmax[2]} }}\n"
        mif += "}\n\n"
    else:
        # There are no subregions in the mesh and only a single BoxAtlas is
        # generated.
        mif += oc.scripts.box_atlas(mesh.region.pmin, mesh.region.pmax, name="main")

    # Define mesh.
    if any(i in mesh.bc for i in "xyz"):
        mif += "# PeriodicRectangularMesh\n"
        mif += "Specify Oxs_PeriodicRectangularMesh:mesh {\n"
        mif += "  cellsize {{ {} {} {} }}\n".format(*mesh.cell)
        mif += "  atlas :main_atlas\n"
        mif += "  periodic {}\n".format("".join(sorted(mesh.bc)))
        mif += "}\n\n"
    else:
        mif += "# RectangularMesh\n"
        mif += "Specify Oxs_RectangularMesh:mesh {\n"
        mif += "  cellsize {{ {} {} {} }}\n".format(*mesh.cell)
        mif += "  atlas :main_atlas\n"
        mif += "}\n\n"

    return mif
