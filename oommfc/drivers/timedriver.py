from .driver import Driver


class TimeDriver(Driver):
    """Time driver.

    Only attributes in ``_allowed_attributes`` can be defined. For details on
    possible values for individual attributes and their default values, please
    refer to ``Oxs_TimeDriver`` documentation (https://math.nist.gov/oommf/).

    Examples
    --------
    1. Defining driver with a keyword argument.

    >>> import oommfc as oc
    ...
    >>> td = oc.TimeDriver(total_iteration_limit=5)

    2. Passing an argument which is not allowed.

    >>> import oommfc as oc
    ...
    >>> td = oc.TimeDriver(myarg=1)
    Traceback (most recent call last):
       ...
    AttributeError: ...

    3. Getting the list of allowed attributes.

    >>> import oommfc as oc
    ...
    >>> td = oc.TimeDriver()
    >>> td._allowed_attributes
    [...]

    """

    _allowed_attributes = [
        "evolver",
        "stopping_dm_dt",
        "stage_iteration_limit",
        "total_iteration_limit",
        "stage_count_check",
        "checkpoint_file",
        "checkpoint_interval",
        "checkpoint_disposal",
        "start_iteration",
        "start_stage",
        "start_stage_iteration",
        "start_stage_start_time",
        "start_stage_elapsed_time",
        "start_last_timestep",
        "normalize_aveM_output",
        "report_max_spin_angle",
        "report_wall_time",
    ]

    def _checkargs(self, **kwargs):
        t, n = kwargs["t"], kwargs["n"]
        if t <= 0:
            msg = f"Cannot drive with {t=}."
            raise ValueError(msg)
        if not isinstance(n, int):
            msg = f"Cannot drive with {type(n)=}."
            raise ValueError(msg)
        if n <= 0:
            msg = f"Cannot drive with {n=}."
            raise ValueError(msg)
