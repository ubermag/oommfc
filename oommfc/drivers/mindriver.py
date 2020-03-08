from .driver import Driver


class MinDriver(Driver):
    """Energy minimisation driver.

    Only parameters which are defined in ``_allowed_attributes`` can be passed.

    Examples
    --------
    1. Defining driver with no keyword arguments.

    >>> import oommfc as oc
    ...
    >>> md = oc.MinDriver()

    2. Passing an argument which is not allowed

    >>> import oommfc as oc
    ...
    >>> md = oc.MinDriver(myarg=3)
    Traceback (most recent call last):
       ...
    AttributeError: ...

    """
    _allowed_attributes = ['evolver',
                           'stopping_mxHxm',
                           'stage_iteration_limit',
                           'total_iteration_limit',
                           'stage_count',
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
        return True  # no kwargs should be checked
