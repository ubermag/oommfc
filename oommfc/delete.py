import os
import shutil


def delete(system, silent=False):
    """Deletes micromagnetic system files.

    This is a convenience function for deleting all of the data associated with
    a system object. More precisely, the directory with name the same as
    ``system.name`` is deleted. If ``silent=True`` is passed, no error is
    raised if the directory does not exist.

    Parameters
    ----------
    system : micromagneticmodel.System

        System whose files are deleted.

    silent : bool, optional

        If ``True``, no error is raised if the directory does not exist.

    Raises
    ------
    FileNotFoundError

        If the directory with ``system.name`` does not exist and
        ``silent=False``.

    Examples
    --------
    1. Delete system files.

    >>> import os
    >>> import oommfc as mc
    >>> import micromagneticmodel as mm
    ...
    >>> system = mm.examples.macrospin()
    >>> mc.delete(system)
    >>> td = mc.TimeDriver()
    >>> td.drive(system, t=1e-12, n=5, save=True)
    Running OOMMF...
    >>> os.path.exists(system.name)
    True
    >>> mc.delete(system)  # deletes directory
    >>> os.path.exists(system.name)
    False

    """
    if os.path.exists(system.name):
        try:
            shutil.rmtree(system.name)
            system.drive_number = 0
        except Exception as e:
            print('Cannot delete system directory.')
            print(e)
    else:
        if not silent:
            msg = f'Directory {system.name} does not exist.'
            raise FileNotFoundError(msg)
