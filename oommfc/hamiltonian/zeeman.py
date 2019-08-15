import oommfc.util as ou
import micromagneticmodel as mm


class Zeeman(mm.Zeeman):
    @property
    def _script(self):
        Hmif, Hname = ou.setup_vector_parameter(self.H, 'ze_H')

        mif = ''
        mif += Hmif
        mif += '# FixedZeeman\n'
        mif += 'Specify Oxs_FixedZeeman {\n'
        mif += f'  field {Hname}\n'
        mif += '}\n\n'

        return mif
