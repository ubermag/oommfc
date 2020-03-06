import re
import os
import glob
import oommfc as oc
import ubermagtable as ut
import micromagneticmodel as mm
import discretisedfield as df


def get_script(term, property):
    if property == 'energy':
        if isinstance(term, mm.Energy):
            return 'RungeKuttaEvolve:evolver:Total energy'
        else:
            mif = getattr(oc.script.energies, f'{term.name}_script')(term)
            cls = re.search(r'Oxs_([\w_]+)', mif).group(1)
            return f'{cls}::{property.capitalize()}'
    elif property == 'effective_field':
        if isinstance(term, mm.Energy):
            return 'Oxs_RungeKuttaEvolve:evolver:Total field'
        else:
            mif = getattr(oc.script.energies, f'{term.name}_script')(term)
            cls = re.search(r'Oxs_([\w_]+)', mif).group(1)
            return f'Oxs_{cls}::Field'
    elif property == 'energy_density':
        if isinstance(term, mm.Energy):
            return 'Oxs_RungeKuttaEvolve:evolver:Total energy density'
        else:
            mif = getattr(oc.script.energies, f'{term.name}_script')(term)
            cls = re.search(r'Oxs_([\w_]+)', mif).group(1)
            return f'Oxs_{cls}::Energy density'


def compute(term, property, system):
    if property == 'energy':
        td = oc.TimeDriver()
        td.drive(system, derive=property)

        dirname = os.path.join(system.name, f'drive-{system.drive_number-1}')
        odt_file = max(glob.iglob(os.path.join(dirname, '*.odt')),
                       key=os.path.getctime)

        table = ut.read(odt_file, rename=False)

        return table[get_script(term, property)][0]

    elif property == 'effective_field':
        td = oc.TimeDriver()
        td.drive(system, derive=get_script(term, property))

        dirname = os.path.join(system.name, f'drive-{system.drive_number-1}')
        ohf_file = max(glob.iglob(os.path.join(dirname, '*.ohf')),
                       key=os.path.getctime)

        return df.Field.fromfile(ohf_file)

    elif property == 'energy_density':
        td = oc.TimeDriver()
        td.drive(system, derive=get_script(term, property))

        dirname = os.path.join(system.name, f'drive-{system.drive_number-1}')
        oef_file = max(glob.iglob(os.path.join(dirname, '*.oef')),
                       key=os.path.getctime)

        return df.Field.fromfile(oef_file)
