import numbers
import oommfc as oc
import discretisedfield as df


def energy_script(container):
    mif = ''
    for term in container:
        mif += globals()[f'{term.name}_script'](term)

    return mif


def exchange_script(term):
    if isinstance(term.A, numbers.Real):
        mif = '# UniformExchange\n'
        mif += 'Specify Oxs_UniformExchange {\n'
        mif += f'  A {term.A}\n'
        mif += '}\n\n'

    elif isinstance(term.A, dict):
        if 'default' in term.A.keys():
            default_value = self.A['default']
        else:
            default_value = 0
        mif = '# Exchange6Ngbr\n'
        mif += 'Specify Oxs_Exchange6Ngbr {\n'
        mif += f'  default_A {default_value}\n'
        mif += '  atlas :main_atlas\n'
        mif += '  A {\n'
        for key, value in term.A.items():
            if key != 'default':
                if ':' in key:
                    region1, region2 = key.split(':')
                else:
                    region1, region2 = key, key
                mif += f'    {region1} {region2} {value}\n'
        mif += '  }\n'
        mif += '}\n\n'

    elif isinstance(term.A, df.Field):
        Amif, Aname = oc.script.setup_scalar_parameter(term.A, 'exchange_A')
        mif = Amif
        mif += '# ExchangePtwise\n'
        mif += 'Specify Oxs_ExchangePtwise {\n'
        mif += f'  A {Aname}\n'
        mif += '}\n\n'

    return mif


def zeeman_script(term):
    Hmif, Hname = oc.script.setup_vector_parameter(term.H, 'zeeman_H')

    mif = ''
    mif += Hmif
    mif += '# FixedZeeman\n'
    mif += 'Specify Oxs_FixedZeeman {\n'
    mif += f'  field {Hname}\n'
    mif += '}\n\n'

    return mif
