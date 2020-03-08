import re
import os
import glob
import oommfc as oc
import ubermagtable as ut
import discretisedfield as df
import micromagneticmodel as mm


def oxs_class(term):
    if isinstance(term, mm.EnergyTerm):
        mif = getattr(oc.scripts.energies, f'{term.name}_script')(term)
        return re.search(r'Oxs_([\w_]+)', mif).group(1)


def schedule_script(func):
    if func.__name__ == 'energy':
        return ''  # Datatable with energies is saved by default.
    elif func.__name__ == 'effective_field':
        if isinstance(func.__self__, mm.Energy):
            output = 'Oxs_RungeKuttaEvolve:evolver:Total field'
        else:
            output = f'Oxs_{oxs_class(func.__self__)}::Field'
    elif func.__name__ == 'density':
        if isinstance(func.__self__, mm.Energy):
            output = 'Oxs_RungeKuttaEvolve:evolver:Total energy density'
        else:
            output = f'Oxs_{oxs_class(func.__self__)}::Energy density'

    return 'Schedule \"{}\" archive Step 1\n'.format(output)


def compute(func, system):
    td = oc.TimeDriver(total_iteration_limit=1)
    td.drive(system, t=1e-25, n=1, compute=schedule_script(func))

    if func.__name__ == 'energy':
        extension = '*.odt'
    elif func.__name__ == 'effective_field':
        extension = '*.ohf'
    elif func.__name__ == 'density':
        extension = '*.oef'
    else:
        msg = f'Computing the value of {func} is not supported.'
        raise ValueError(msg)

    dirname = os.path.join(system.name, f'compute-{system.drive_number-1}')
    output_file = max(glob.iglob(os.path.join(dirname, extension)),
                      key=os.path.getctime)

    if func.__name__ == 'energy':
        table = ut.read(output_file, rename=False)
        if isinstance(func.__self__, mm.Energy):
            return table['RungeKuttaEvolve:evolver:Total energy'][0]
        else:
            return table[f'{oxs_class(func.__self__)}::Energy'][0]
    else:
        return df.Field.fromfile(output_file)
