import os
import glob
import oommfc as oc
import discretisedfield as df
import micromagneticmodel as mm


class Data(mm.Data):
    _dict = {"Demag": "Oxs_Demag",
             "Exchange": "Oxs_UniformExchange",
             "UniaxialAnisotropy": "Oxs_UniaxialAnisotropy",
             "Zeeman": "Oxs_FixedZeeman"}
    @property
    def effective_field(self):
        
        derive = "{}::Field".format(self._dict[self.interaction])

        td = oc.TimeDriver()
        td.drive(self.system, derive=derive)

        dirname = os.path.join(self.system.name, "")
        last_ohf_file = max(glob.iglob("{}*.ohf".format(dirname)),
                            key=os.path.getctime)

        return df.read_oommf_file(last_ohf_file)
