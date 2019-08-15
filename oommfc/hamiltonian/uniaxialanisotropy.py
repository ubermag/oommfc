import oommfc.util as ou
import micromagneticmodel as mm


class UniaxialAnisotropy(mm.UniaxialAnisotropy):
    @property
    def _script(self):
        k1mif, k1name = ou.setup_scalar_parameter(self.K1, 'ua_K1')
        umif, uname = ou.setup_vector_parameter(self.u, 'ua_u')

        mif = ''
        mif += k1mif
        mif += umif
        mif += '# UniaxialAnisotropy\n'
        mif += 'Specify Oxs_UniaxialAnisotropy {\n'
        mif += f'  K1 {k1name}\n'
        mif += f'  axis {uname}\n'
        mif += '}\n\n'

        return mif
