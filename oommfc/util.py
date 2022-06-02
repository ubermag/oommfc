import contextlib
import os


@contextlib.contextmanager
def changedir(dirname):
    """Context manager for changing directory."""
    cwd = os.getcwd()
    os.chdir(dirname)
    try:
        yield
    finally:
        os.chdir(cwd)
