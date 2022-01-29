import oommfc as oc


def system_script(system, ovf_format, **kwargs):
    if ovf_format == 'bin8':
        output_format = 'binary 8'
    elif ovf_format == 'bin4':
        output_format = 'binary 4'
    elif ovf_format == 'txt':
        output_format = 'text %#.15g'
    else:
        raise ValueError(f'Invalid {ovf_format=}.')
    mif = '# MIF 2.2\n\n'
    # Output options
    mif += 'SetOptions {\n'
    mif += f'  basename {system.name}\n'
    mif += '  scalar_output_format %.12g\n'
    mif += f'  scalar_field_output_format {{{output_format}}}\n'
    mif += f'  vector_field_output_format {{{output_format}}}\n'
    mif += '}\n\n'

    # Mesh and energy scripts.
    mif += oc.scripts.mesh_script(system.m.mesh)
    mif += oc.scripts.energy_script(system)

    # Magnetisation script.
    m0mif, _, _ = oc.scripts.setup_m0(system.m, 'm0')
    mif += m0mif

    return mif
