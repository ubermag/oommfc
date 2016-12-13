import os
import glob
import oommfc as oc
import discretisedfield as df
import micromagneticmodel as mm


class Data(mm.Data):
    @property
    def effective_field(self):
        _dict = {"Demag": "Oxs_Demag::Field",
                 "Exchange": "Oxs_UniformExchange::Field",
                 "UniaxialAnisotropy": "Oxs_UniaxialAnisotropy::Field",
                 "Zeeman": "Oxs_FixedZeeman::Field",
                 "Hamiltonian": "Oxs_RungeKuttaEvolve:evolver:Total field"}

        td = oc.TimeDriver()
        td.drive(self.system, derive=_dict[self.interaction])

        dirname = os.path.join(self.system.name, "")
        last_ohf_file = max(glob.iglob("{}*.ohf".format(dirname)),
                            key=os.path.getctime)

        return df.read_oommf_file(last_ohf_file)

    @property
    def energy(self):
        pass
