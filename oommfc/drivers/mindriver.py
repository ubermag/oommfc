from .driver import Driver


class MinDriver(Driver):
    """Energy minimisation driver.

    Only attributes in ``_allowed_attributes`` can be defined. For details on
    possible values for individual attributes and their default values, please
    refer to ``Oxs_MinDriver`` documentation (https://math.nist.gov/oommf/).

    Examples
    --------
    1. Defining driver with a keyword argument.

    >>> import oommfc as oc
    ...
    >>> md = oc.MinDriver(stopping_mxHxm=0.01)

    2. Passing an argument which is not allowed.

    >>> import oommfc as oc
    ...
    >>> md = oc.MinDriver(myarg=1)
    Traceback (most recent call last):
       ...
    AttributeError: ...

    3. Getting the list of allowed attributes.

    >>> import oommfc as oc
    ...
    >>> md = oc.MinDriver()
    >>> md._allowed_attributes
    [...]

    """

    _allowed_attributes = [
        "evolver",
        "stopping_mxHxm",
        "stage_iteration_limit",
        "total_iteration_limit",
        "stage_count",
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
        pass  # no kwargs should be checked
