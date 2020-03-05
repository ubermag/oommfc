import numbers
import oommfc as oc
import oommfc.util as ou
import discretisedfield as df


def energy_script(container):
    mif = ''
    for term in container:
        mif += globals()[f'{term.name}_script'](term)  #]getattr(oc, f'{term.name}_script')(term)

    return mif


def exchange_script(term):
    """Returns calculator's script.

    Parameters
    ----------
    mesh : micromagneticmodel.Exchange

        Exchange object.

    Returns
    -------
    str

        Calculator's script.

    Examples
    --------
    1. Getting calculator's script.

    >>> import micromagneticmodel as mm
    >>> import oommfc as oc
    ...
    >>> term = mm.Exchange(A=1e-12)
    >>> oc.script.exchange(term)
    ...

    """
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
        Amif, Aname = ou.setup_scalar_parameter(term.A, 'exchange_A')
        mif = Amif
        mif += '# ExchangePtwise\n'
        mif += 'Specify Oxs_ExchangePtwise {\n'
        mif += f'  A {Aname}\n'
        mif += '}\n\n'

    return mif
