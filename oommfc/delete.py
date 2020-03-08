import os
import shutil


def delete(system):
    """Deletes micromagnetic system files.

    Parameters
    ----------
    system : micromagneticmodel.System

        System whose files are deleted.

    Examples
    --------
    1. Delete system files.

    >>> import oommfc as oc
    >>> import micromagneticmodel as mm
    ...
    >>> system = mm.examples.macrospin()
    >>> md = oc.TimeDriver()
    >>> md.drive(system, save=True)
    >>> oc.delete(system)  # deletes directory

    """
    if os.path.exists(system.name):
        shutil.rmtree(system.name)
    else:
        msg = f'No directory {self.name} exists.'
        raise FileNotFoundError(msg)
