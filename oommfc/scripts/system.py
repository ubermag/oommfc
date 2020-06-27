import oommfc as oc


def system_script(system, **kwargs):
    mif = '# MIF 2.2\n\n'
    # Output options
    mif += 'SetOptions {\n'
    mif += f'  basename {system.name}\n'
    mif += '  scalar_output_format %.12g\n'
    mif += '  scalar_field_output_format {text %#.15g}\n'
    mif += '  vector_field_output_format {text %#.15g}\n'
    mif += '}\n\n'

    # Mesh and energy scripts.
    mif += oc.scripts.mesh_script(system.m.mesh)
    mif += oc.scripts.energy_script(system)

    # Magnetisation script.
    m0mif, _, _ = oc.scripts.setup_m0(system.m, 'm0')
    mif += m0mif

    return mif
