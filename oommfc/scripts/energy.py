import sys
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
            default_value = term.A['default']
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
        Amif, Aname = oc.scripts.setup_scalar_parameter(term.A, 'exchange_A')
        mif = Amif
        mif += '# ExchangePtwise\n'
        mif += 'Specify Oxs_ExchangePtwise {\n'
        mif += f'  A {Aname}\n'
        mif += '}\n\n'

    return mif


def zeeman_script(term):
    Hmif, Hname = oc.scripts.setup_vector_parameter(term.H, 'zeeman_H')

    mif = ''
    mif += Hmif
    mif += '# FixedZeeman\n'
    mif += 'Specify Oxs_FixedZeeman {\n'
    mif += f'  field {Hname}\n'
    mif += '}\n\n'

    return mif


def demag_script(term):
    mif = '# Demag\n'
    mif += 'Specify Oxs_Demag {\n'
    if hasattr(term, 'asymptotic_radius'):
        mif += f'  asymptotic_radius {term.asymptotic_radius}\n'
    mif += '}\n\n'

    return mif


def dmi_script(term):
    if term.crystalclass in ['T', 'O'] and sys.platform != 'win32':
        oxs = 'Oxs_DMI_T'
    elif term.crystalclass == 'D2d' and sys.platform != 'win32':
        oxs = 'Oxs_DMI_D2d'
    elif term.crystalclass == 'Cnv' and sys.platform != 'win32':
        oxs = 'Oxs_DMI_Cnv'
    # The following lines cannot be accessed on TravisCI, where coverage is
    # evaluated. Therefore, those lines are excluded from coverage.
    elif (term.crystalclass == 'Cnv' and
          sys.platform == 'win32'):  # pragma: no cover
        oxs = 'Oxs_DMExchange6Ngbr'  # pragma: no cover
    else:
        raise ValueError(f'The {term.crystalclass} crystal '
                         f'class is not supported on {sys.platform} '
                         'platform.')  # pragma: no cover

    mif = f'# DMI of crystallographic class {term.crystalclass}\n'
    mif += f'Specify {oxs} {{\n'

    if isinstance(term.D, numbers.Real):
        mif += f'  default_D {term.D}\n'
        mif += '  atlas :main_atlas\n'
        mif += '  D {\n'
        mif += f'    main main {term.D}\n'
        mif += '  }\n'
        mif += '}\n\n'

    elif isinstance(term.D, dict):
        if 'default' in term.D.keys():
            default_value = term.D['default']
        else:
            default_value = 0
        mif += f'  default_D {default_value}\n'
        mif += '  atlas :main_atlas\n'
        mif += '  D {\n'
        for key, value in term.D.items():
            if key != 'default':
                if ':' in key:
                    region1, region2 = key.split(':')
                else:
                    region1, region2 = key, key
                mif += f'    {region1} {region2} {value}\n'
        mif += '  }\n'
        mif += '}\n\n'

    return mif


def uniaxialanisotropy_script(term):
    kmif, kname = oc.scripts.setup_scalar_parameter(term.K, 'ua_K')
    umif, uname = oc.scripts.setup_vector_parameter(term.u, 'ua_u')

    mif = ''
    mif += kmif
    mif += umif
    mif += '# UniaxialAnisotropy\n'
    mif += 'Specify Oxs_UniaxialAnisotropy {\n'
    mif += f'  K1 {kname}\n'
    mif += f'  axis {uname}\n'
    mif += '}\n\n'

    return mif


def cubicanisotropy_script(term):
    kmif, kname = oc.scripts.setup_scalar_parameter(term.K, 'ca_K')
    u1mif, u1name = oc.scripts.setup_vector_parameter(term.u1, 'ca_u1')
    u2mif, u2name = oc.scripts.setup_vector_parameter(term.u2, 'ca_u2')

    mif = ''
    mif += kmif
    mif += u1mif
    mif += u2mif
    mif += '# CubicAnisotropy\n'
    mif += 'Specify Oxs_CubicAnisotropy {\n'
    mif += f'  K1 {kname}\n'
    mif += f'  axis1 {u1name}\n'
    mif += f'  axis2 {u2name}\n'
    mif += '}\n\n'

    return mif


def magnetoelastic_script(term):
    B1mif, B1name = oc.scripts.setup_scalar_parameter(term.B1, 'mel_B1')
    B2mif, B2name = oc.scripts.setup_scalar_parameter(term.B2, 'mel_B2')
    ediagmif, ediagname = oc.scripts.setup_vector_parameter(
        term.e_diag, 'mel_ediag')
    eoffdiagmif, eoffdiagname = oc.scripts.setup_vector_parameter(
        term.e_offdiag, 'mel_eoffdiag')

    mif = ''
    mif += B1mif
    mif += B2mif
    mif += ediagmif
    mif += eoffdiagmif
    mif += '# MagnetoElastic\n'
    mif += 'Specify YY_FixedMEL {\n'
    mif += f'  B1 {B1name}\n'
    mif += f'  B2 {B2name}\n'
    mif += f'  e_diag_field {ediagname}\n'
    mif += f'  e_offdiag_field {eoffdiagname}\n'
    mif += '}\n\n'

    return mif
