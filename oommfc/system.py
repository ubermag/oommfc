import os
import shutil
import micromagneticmodel as mm


class System(mm.System):
    """System class.

    This class is used for defining a micromagnetic system. In
    order to uniquely define a micromagnetic system, the following
    three parameters must be provided:

    - Name
    - Hamiltonian
    - Dynamics equation
    - Initial magnetisation configuration

    When driven, a directory with the same name (`oommfc.system.name`)
    will be created.

    Parameters
    ----------
    hamiltonian : oommfc.Hamiltonian, optional
        Hamiltonian as a sum of different energy terms.
    dynamics : oommfc.Dynamics, optional
        Dynamics as a sum of different dynamics terms.
    m : disretisedfield.Field, optional
        Initial magnetisation configuration as a three-dimensional
        field.
    name : str
        Name of the system.

    Raises
    ------
    AttributeError
        If a keyword argument which is not in the parameter list
        is passed.

    Examples
    --------
    1. Setting a simple system class

    >>> import oommfc as oc
    >>> import discretisedfield as df
    ...
    >>> p1 = (0, 0, 0)
    >>> p2 = (10e-9, 10e-9, 10e-9)
    >>> n = (5, 5, 5)
    >>> mesh = oc.Mesh(p1=p1, p2=p2, n=n)
    ...
    >>> system = oc.System(name='mysystem')
    >>> system.m = df.Field(mesh, dim=3, value=(0, 0, 1), norm=1e6)
    >>> system.hamiltonian = oc.Exchange(A=1e-11) + oc.Demag()
    >>> system.dynamics = oc.Precession(gamma=mm.consts.gamma0) + \
            oc.Damping(alpha=0.1)

    """
    def total_energy(self):
        """Total energy of the system.

        If the system was already driven, this method returns its
        energy by reading it from the datatable `system.dt`.

        """
        return self.dt.tail(1)['E'][0]

    def delete(self):
        """Delete all system related files.

        When a system object is driven using a Driver, a directory
        with `system.name` name is created where different run files
        are created. This function deletes those files if they exist.

        """
        if os.path.exists(f'{self.name}'):
            shutil.rmtree(self.name)

    @property
    def _script(self):
        mif = self.m.mesh._script
        mif += self.hamiltonian._script

        return mif
