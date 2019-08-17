import numbers
import oommfc.util as ou
import discretisedfield as df
import micromagneticmodel as mm


class Exchange(mm.Exchange):
    @property
    def _script(self):
        if isinstance(self.A, numbers.Real):
            mif = '# UniformExchange\n'
            mif += 'Specify Oxs_UniformExchange {\n'
            mif += f'  A {self.A}\n'
            mif += '}\n\n'
        elif isinstance(self.A, dict):
            if 'default' in self.A.keys():
                default_value = self.A['default']
            else:
                default_value = 0
            mif = '# Exchange6Ngbr\n'
            mif += 'Specify Oxs_Exchange6Ngbr {\n'
            mif += f'  default_A {default_value}\n'
            mif += '  atlas :main_atlas\n'
            mif += '  A {\n'
            for key, value in self.A.items():
                if key != 'default':
                    if ':' in key:
                        region1, region2 = key.split(':')
                    else:
                        region1, region2 = key, key
                    mif += f'    {region1} {region2} {value}\n'
            mif += '  }\n'
            mif += '}\n\n'
        elif isinstance(self.A, df.Field):
            Amif, Aname = ou.setup_scalar_parameter(self.A, 'ex_A')
            mif = Amif
            mif += '# ExchangePtwise\n'
            mif += 'Specify Oxs_ExchangePtwise {\n'
            mif += f'  A {Aname}\n'
            mif += '}\n\n'

        return mif
