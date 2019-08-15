def mif_file_vector_field(filename, name, atlas):
    mif = f'# {name} file\n'
    mif += f'Specify Oxs_FileVectorField:{name} {{\n'
    mif += f'   file {filename}\n'
    mif += f'   atlas :{atlas}\n'
    mif += '}\n\n'

    return mif

def mif_vec_mag_scalar_field(filename):
    pass
