import numpy as np

from .driver import Driver


class HysteresisDriver(Driver):
    """Hysteresis driver.

    Only attributes in ``_allowed_attributes`` can be defined. For details on
    possible values for individual attributes and their default values, please
    refer to ``Oxs_MinDriver`` documentation (https://math.nist.gov/oommf/).

    Examples
    --------
    1. Defining driver with a keyword argument.

    >>> import oommfc as mc
    ...
    >>> hd = mc.HysteresisDriver(stopping_mxHxm=0.01)

    2. Passing an argument which is not allowed.

    >>> import oommfc as mc
    ...
    >>> md = mc.HysteresisDriver(myarg=1)
    Traceback (most recent call last):
       ...
    AttributeError: ...

    3. Getting the list of allowed attributes.

    >>> import oommfc as mc
    ...
    >>> hd = mc.HysteresisDriver()
    >>> hd._allowed_attributes
    [...]

    4. How to define multiple steps with this driver.
    >>> import micromagneticmodel as mm
    >>> import oommfc as oc
    >>> system = mm.examples.macrospin()
    >>> sd = oc.HysteresisDriver()
    >>> H = 1 / mm.consts.mu0
    >>> sd.drive(system, Hsteps=[
    ...    [(0, 0, 0), (0, 0, H), 10],
    ...    [(0, 0, H), (0, 0, -H), 10],
    ...    [(0, 0, -H), (0, 0, 0), 10],
    ... ])
    Running OOMMF ...

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

    def _checkargs(self, kwargs):
        if any(item in kwargs for item in ["Hmin", "Hmax", "n"]) and "Hsteps" in kwargs:
            # both Hsteps and (Hmin, Hmax, n) are defined, which is not allowed
            msg = "Cannot define both (Hmin, Hmax, n) and Hsteps."
            raise ValueError(msg)

        if all(item in kwargs for item in ["Hmin", "Hmax", "n"]):
            # case of a symmetric hysteresis simulation
            # construct symmetric Hsteps from (Hmin, Hmax, n)
            kwargs["Hsteps"] = [
                [kwargs["Hmin"], kwargs["Hmax"], kwargs["n"]],
                [kwargs["Hmax"], kwargs["Hmin"], kwargs["n"]],
            ]
            for key in ["Hmin", "Hmax", "n"]:
                kwargs.pop(key)

        if "Hsteps" in kwargs:
            # case of a stepped hysteresis simulation
            for step in kwargs["Hsteps"]:
                if len(step) != 3:
                    msg = (
                        "Each list item in Hsteps must have 3 entries: Hstart, Hend, n."
                    )
                    raise ValueError(msg)
                self._checkvalues(step[0], step[1], step[2])
        else:
            msg = (
                "Cannot drive without a full definition of (Hmin, Hmax, n) xor Hsteps."
            )
            return ValueError(msg)

    @staticmethod
    def _checkvalues(Hmin, Hmax, n):
        for item in [Hmin, Hmax]:
            if not isinstance(item, (list, tuple, np.ndarray)):
                msg = "Hmin and Hmax must have array_like values."
                raise ValueError(msg)
            if len(item) != 3:
                msg = "Hmin and Hmax must have length 3."
                raise ValueError(msg)
        if not isinstance(n, int):
            msg = f"Cannot drive with {type(n)=}."
            raise ValueError(msg)
        if n - 1 <= 0:  # OOMMF counts steps, not points (n -> n-1)
            msg = f"Cannot drive with {n=}."
            raise ValueError(msg)

    def _check_system(self, system):
        """Checks the system has energy in it"""
        if len(system.energy) == 0:
            raise RuntimeError("System's energy is not defined")

    @property
    def _x(self):
        return "B_hysteresis"
