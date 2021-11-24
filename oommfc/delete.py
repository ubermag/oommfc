import os
import shutil
import sys
import oommfc as oc


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
        if sys.platform == 'win32':
            # on Windows the running oommf process prevents deletion
            oc.runner.runner._kill()
        try:
            shutil.rmtree(system.name, onerror=_onerror)
            system.drive_number = 0
        except Exception as e:
            print('Cannot delete system directory.')
            print(e)
    else:
        if not silent:
            msg = f'Directory {system.name} does not exist.'
            raise FileNotFoundError(msg)


def _onerror(func, path, exc_info):
    """
    Error handler for ``shutil.rmtree``.

    From https://stackoverflow.com/a/2656405 and
    http://www.voidspace.org.uk/downloads/pathutils.py

    If the error is due to an access error (read only file)
    it attempts to add write permission and then retries.

    If the error is for another reason it re-raises the error.

    Usage : ``shutil.rmtree(path, onerror=onerror)``
    """
    import stat
    # Is the error an access error?
    if not os.access(path, os.W_OK):
        os.chmod(path, stat.S_IWUSR)
        func(path)
    else:
        raise
