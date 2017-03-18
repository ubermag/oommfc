import micromagneticmodel as mm


class Demag(mm.Demag):
    @property
    def _script(self):
        mif = "# Demag\n"
        mif += "Specify Oxs_Demag {}\n\n"

        return mif
