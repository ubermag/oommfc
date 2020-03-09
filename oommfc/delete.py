import os
import shutil


def delete(system):
    """Deletes micromagnetic system files.

    After the system is driven, if ``save=True`` is passed, the files obtained
    from an OOMMF run are saved in the current directory. ``oommfc.delete`` is
    a convenience function for deleting all of them. More precisely, the
    directory with name the same as ``system.name`` is deleted.

    Parameters
    ----------
    system : micromagneticmodel.System

        System whose files are deleted.

    Raises
    ------
    FileNotFoundError

        If the directory with ``system.name`` does not exist.

    Examples
    --------
    1. Delete system files.

    >>> import os
    >>> import oommfc as oc
    >>> import micromagneticmodel as mm
    ...
    >>> system = mm.examples.macrospin()
    >>> td = oc.TimeDriver()
    >>> td.drive(system, t=1e-12, n=5, save=True)
    Running OOMMF...
    >>> os.path.exists(system.name)
    True
    >>> oc.delete(system)  # deletes directory
    >>> os.path.exists(system.name)
    False

    """
    if os.path.exists(system.name):
        shutil.rmtree(system.name)
    else:
        msg = f'Directory {system.name} does not exist.'
        raise FileNotFoundError(msg)
