import oommfc as oc
import discretisedfield as df
import micromagneticmodel as mm


class UniaxialAnisotropy(mm.UniaxialAnisotropy):
    @property
    def _script(self):
        mif = ''
        if isinstance(self.K1, df.Field):
            if self.K1.dim != 1:
                msg = 'Parameter must be a scalar field'
                raise ValueError(msg)
            self.K1.write('uniaxialanisotropy_k1.omf', extend_scalar=True)
            mif += oc.util.mif_file_vector_field('uniaxialanisotropy_k1.omf',
                                                 'uniaxialanisotropy_k1')
            mif += oc.util.mif_vec_mag_scalar_field('uniaxialanisotropy_k1',
                                                    'uniaxialanisotropy_k1_norm')
            K1_repr = 'uniaxialanisotropy_k1_norm'
                
            
        mif = "# UniaxialAnisotropy\n"
        if self.K2 == 0:
            mif += "Specify Oxs_UniaxialAnisotropy {\n"
            mif += "  K1 {}\n".format(self.K1)
            mif += "  axis {{{} {} {}}}\n".format(*self.u)
            mif += "}\n\n"
        else:
            mif += "Specify Southampton_UniaxialAnisotropy4 {\n"
            mif += "  K1 {}\n".format(self.K1)
            mif += "  K2 {}\n".format(self.K2)
            mif += "  axis {{{} {} {}}}\n".format(*self.u)
            mif += "}\n\n"

        return mif
