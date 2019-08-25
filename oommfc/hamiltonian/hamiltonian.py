import micromagneticmodel as mm


class Hamiltonian(mm.Hamiltonian):
    """Hamiltonian

    This class implements the sum of individual energy terms. It is
    obtained as a result of addition of two or more energy terms.

    Examples
    --------
    1. Adding an energy term to the Hamiltonian.

    >>> import oommfc as oc
    ...
    >>> hamiltonian = oc.Hamiltonian()
    >>> hamiltonian += mm.DMI(D=1e-3, crystalclass='Cnv')

    2. Creating the Hamiltoninan as a sum of two energy terms

    >>> import oommfc as oc
    ...
    >>> hamiltonian = oc.Exchange(A=1e-12) + oc.Zeeman(H=(0, 0, 1e6))

    """
    @property
    def _script(self):
        mif = ''
        for term in self.terms:
            mif += term._script

        return mif
