import oommfc as oc
from .driver import Driver
import micromagneticmodel as mm


class TimeDriver(Driver):
    """Time driver.

    This class is used for collecting additional parameters, which
    could be passed to `Oxs_TimeDriver`. Only parameters which are
    defined in `_allowed_kwargs` can be passed.

    Examples
    --------
    1. Defining driver

    >>> import oommfc as oc
    ...
    >>> td = oc.TimeDriver()

    2. Passing an argument which is not allowed

    >>> import oommfc as oc
    ...
    >>> td = oc.TimeDriver(myarg=3)
    Traceback (most recent call last):
       ...
    AttributeError: ...

    """
    _allowed_attributes = ['evolver',
                           'stopping_dm_dt',
                           'stage_iteration_limit',
                           'total_iteration_limit',
                           'stage_count_check',
                           'checkpoint_file',
                           'checkpoint_interval',
                           'checkpoint_disposal',
                           'start_iteration',
                           'start_stage',
                           'start_stage_iteration',
                           'start_stage_start_time',
                           'start_stage_elapsed_time',
                           'start_last_timestep',
                           'normalize_aveM_output',
                           'report_max_spin_angle',
                           'report_wall_time']

    def _checkargs(self, **kwargs):
        if 'compute' not in kwargs:
            if kwargs['t'] <= 0:
                msg = 'Positive simulation time expected (t>0).'
                raise ValueError(msg)
            if kwargs['n'] <= 0 or not isinstance(kwargs['n'], int):
                msg = 'Positive integer number of steps expected (n>0)'
                raise ValueError(msg)
