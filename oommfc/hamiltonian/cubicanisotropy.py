import oommfc.util as ou
import micromagneticmodel as mm


class CubicAnisotropy(mm.CubicAnisotropy):
    @property
    def _script(self):
        k1mif, k1name = ou.setup_scalar_parameter(self.K1, 'ca_K1')
        u1mif, u1name = ou.setup_vector_parameter(self.u1, 'ca_u1')
        u2mif, u2name = ou.setup_vector_parameter(self.u2, 'ca_u2')

        mif = ''
        mif += k1mif
        mif += u1mif
        mif += u2mif
        mif += '# CubicAnisotropy\n'
        mif += 'Specify Oxs_CubicAnisotropy {\n'
        mif += f'  K1 {k1name}\n'
        mif += f'  axis1 {u1name}\n'
        mif += f'  axis2 {u2name}\n'
        mif += '}\n\n'

        return mif
