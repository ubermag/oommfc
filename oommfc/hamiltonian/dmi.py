import sys
import numbers
import micromagneticmodel as mm


class DMI(mm.DMI):
    @property
    def _script(self):
        if self.crystalclass in ['t', 'o'] and sys.platform != 'win32':
            oxs = 'Oxs_DMI_T'
        elif self.crystalclass == 'd2d' and sys.platform != 'win32':
            oxs = 'Oxs_DMI_D2d'
        elif self.crystalclass == 'cnv' and sys.platform != 'win32':
            oxs = 'Oxs_DMI_Cnv'
        elif self.crystalclass == 'cnv' and sys.platform == 'win32':
            oxs = 'Oxs_DMExchange6Ngbr'
        else:
            raise ValueError(f'The {self.crystalclass} crystal class is not '
                             f'supported on {sys.platform} platform.')

        mif = f'# DMI of crystallographic class {self.crystalclass}\n'
        mif += f'Specify {oxs} {{\n'
        if isinstance(self.D, numbers.Real):
            mif += f'  default_D {self.D}\n'
            mif += '  atlas :main_atlas\n'
            mif += '  D {\n'
            mif += f'    main main {self.D}\n'
            mif += '  }\n'
            mif += '}\n\n'
        elif isinstance(self.D, dict):
            if 'default' in self.D.keys():
                default_value = self.D['default']
            else:
                default_value = 0
            mif += f'  default_D {default_value}\n'
            mif += '  atlas :main_atlas\n'
            mif += '  D {\n'
            for key, value in self.D.items():
                if key != 'default':
                    if ':' in key:
                        region1, region2 = key.split(':')
                    else:
                        region1, region2 = key, key
                    mif += f'    {region1} {region2} {value}\n'
            mif += '  }\n'
            mif += '}\n\n'
        else:
            msg = f'Type {type(self.D)} not supported.'
            raise ValueError(msg)

        return mif
