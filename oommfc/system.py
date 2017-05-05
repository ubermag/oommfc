import micromagneticmodel as mm


class System(mm.System):
    """Micromagnetic system oject.

    Parameters
    ----------
    name : str

    Examples
    --------
    Creating a simple system object.

    >>> import oommfc as oc
    >>> system = oc.System(name="my_system")

    """
    @property
    def _script(self):
        mif = self.m.mesh._script
        mif += self.hamiltonian._script
        return mif

    def total_energy(self):
        return self.dt.tail(1)["E"][0]
