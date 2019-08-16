import numbers
import numpy as np
import discretisedfield as df


def mif_file_vector_field(filename, name, atlas='main_atlas'):
    mif = f'# {name} file\n'
    mif += f'Specify Oxs_FileVectorField:{name} {{\n'
    mif += f'   file {filename}\n'
    mif += f'   atlas :{atlas}\n'
    mif += '}\n\n'

    return mif


def mif_vec_mag_scalar_field(field, name):
    mif = f'# {name}\n'
    mif += f'Specify Oxs_VecMagScalarField:{name} {{\n'
    mif += f'    field :{field}\n'
    mif += '}\n\n'

    return mif


def mif_box_atlas(pmin, pmax, name='atlas'):
    mif = f'# BoxAtlas for {name}_atlas\n'
    mif += f'Specify Oxs_BoxAtlas:{name}_atlas {{\n'
    mif += f'  xrange {{{pmin[0]} {pmax[0]}}}\n'
    mif += f'  yrange {{{pmin[1]} {pmax[1]}}}\n'
    mif += f'  zrange {{{pmin[2]} {pmax[2]}}}\n'
    mif += f'  name {name}\n'
    mif += '}\n\n'

    return mif


def setup_scalar_parameter(parameter, name):
    if isinstance(parameter, df.Field):
        if parameter.dim != 1:
            msg = 'Parameter must be a scalar (dim=1) field.'
            raise ValueError(msg)
        parameter.write(f'{name}.ovf', extend_scalar=True)
        mif = mif_file_vector_field(f'{name}.ovf', f'{name}')
        mif += mif_vec_mag_scalar_field(f'{name}', f'{name}_norm')
        return mif, f'{name}_norm'
    elif isinstance(parameter, numbers.Real):
        return '', f'{parameter}'


def setup_vector_parameter(parameter, name):
    if isinstance(parameter, df.Field):
        if parameter.dim != 3:
            msg = 'Parameter must be a vector (dim=3) field.'
            raise ValueError(msg)
        parameter.write(f'{name}.ovf')
        mif = mif_file_vector_field(f'{name}.ovf', f'{name}')
        return mif, f'{name}'
    elif isinstance(parameter, (tuple, list, np.ndarray)):
        return '', '{{{} {} {}}}'.format(*parameter)
