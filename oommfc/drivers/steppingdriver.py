import numpy as np

from .driver import Driver


class SteppingDriver(Driver):
    """Stepping hysteresis driver.

    Multiple sweeps from any ``Hmin`` to ``Hmax`` with n steps are possible.
    Only attributes in ``_allowed_attributes`` can be defined. For details on
    possible values for individual attributes and their default values, please
    refer to ``Oxs_MinDriver`` documentation (https://math.nist.gov/oommf/).

    Examples
    --------
    1. Defining driver with a keyword argument.

    >>> import oommfc as oc
    ...
    >>> sd = oc.SteppingDriver(stopping_mxHxm=0.01)

    2. Passing an argument which is not allowed.

    >>> import oommfc as oc
    ...
    >>> sd = oc.SteppingDriver(myarg=1)
    Traceback (most recent call last):
       ...
    AttributeError: ...

    3. Getting the list of allowed attributes.

    >>> import oommfc as oc
    ...
    >>> sd = oc.SteppingDriver()
    >>> sd._allowed_attributes
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
        for Hstart, Hstop, n in kwargs["steps"]:
            for i in [Hstart, Hstop]:
                if not isinstance(i, (list, tuple, np.ndarray)):
                    msg = "Hstart and Hstop must have array_like values."
                    raise ValueError(msg)
                if len(i) != 3:
                    msg = "Hmin and Hmax must have length 3."
                    raise ValueError(msg)
            if not isinstance(n, int):
                msg = f"Cannot drive with {type(n)=}."
                raise ValueError(msg)
            if n <= 1:  # OOMMF counts steps, not points (n -> n-1)
                msg = f"Cannot drive with {n=}."
                raise ValueError(msg)

    @property
    def _x(self):
        return "B_hysteresis"
