import oommfc as oc
import micromagneticmodel as mm


class SpinTEvolver(mm.Evolver):
    """Zhang-Li evolver.

    This class is used for collecting additional parameters, which
    cannot be extracted from the dynamics equation, but could be
    passed to `Anv_SpinTEvolve`. Only parameters which are
    defined in `_allowed_kwargs` can be passed.

    Examples
    --------
    1. Defining evolver

    >>> import oommfc as oc
    ...
    >>> evolver = oc.SpinTEvolver(method='rkf54s')

    2. Passing an argument which is not allowed

    >>> import oommfc as oc
    ...
    >>> evolver = oc.SpinTEvolver(myarg=3)
    Traceback (most recent call last):
       ...
    AttributeError: ...

    """
    _allowed_attributes = ['alpha',
                           'gamma_LL',
                           'gamma_G',
                           'do_precess',
                           'u',
                           'beta',
                           'method']
