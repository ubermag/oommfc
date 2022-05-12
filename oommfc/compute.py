import glob
import os
import re

import discretisedfield as df
import micromagneticmodel as mm
import ubermagtable as ut

import oommfc as oc


def oxs_class(term, system):
    """Extract the OOMMF ``Oxs_`` class name of an individual term."""
    mif = getattr(oc.scripts.energy, f"{term.name}_script")(term, system)
    return re.search(r"Oxs_([\w_]+)", mif).group(1)


def schedule_script(func, system):
    """Generate OOMMF ``Schedule...`` line for saving an individual value."""
    if func.__name__ == "energy":
        return ""  # Datatable with energies is saved by default.
    elif func.__name__ == "effective_field":
        if isinstance(func.__self__, mm.Energy):
            output = "Oxs_RungeKuttaEvolve:evolver:Total field"
        else:
            output = (
                f"Oxs_{oxs_class(func.__self__, system)}:{func.__self__.name}:Field"
            )
    elif func.__name__ == "density":
        if isinstance(func.__self__, mm.Energy):
            output = "Oxs_RungeKuttaEvolve:evolver:Total energy density"
        else:
            output = (
                f"Oxs_{oxs_class(func.__self__, system)}:"
                f"{func.__self__.name}:Energy density"
            )
    else:
        msg = f"Computing the value of {func} is not supported."
        raise ValueError(msg)

    return 'Schedule "{}" archive Step 1\n'.format(output)


def compute(func, system, /, verbose=1):
    """Computes a particular value of an energy term or energy container
    (``energy``, ``density``, or ``effective_field``).

    Parameters
    ----------
    func : callable

        A property of an energy term or an energy container.

    system : micromagneticmodel.System

        Micromagnetic system for which the property is calculated.

    verbose : int, optional

        If ``verbose=0``, no output is printed. For ``verbose>=1``
        information about the OOMMF runner and the runtime is printed to
        stdout. Defaults is ``verbose=1``.

    Returns
    -------
    numbers.Real, discretisedfield.Field

        Resulting value.

    Examples
    --------
    1. Computing values of energy terms.

    >>> import micromagneticmodel as mm
    >>> import oommfc as oc
    ...
    >>> system = mm.examples.macrospin()
    >>> oc.compute(system.energy.zeeman.energy, system)
    Running OOMMF...
    -8.8...e-22
    >>> oc.compute(system.energy.effective_field, system)
    Running OOMMF...
    Field(...)
    >>> oc.compute(system.energy.density, system)
    Running OOMMF...
    Field(...)

    """
    td = oc.TimeDriver(total_iteration_limit=1)
    try:
        td.drive(
            system,
            t=1e-25,
            n=1,
            append=True,
            compute=schedule_script(func, system),
            verbose=verbose,
        )
    except RuntimeError:
        msg = (
            "`oc.compute` does not support finite temperature."
            f" (Temperature is specified as {system.T=})"
        )
        raise RuntimeError(msg)

    if func.__name__ == "energy":
        extension = "*.odt"
    elif func.__name__ == "effective_field":
        extension = "*.ohf"
    elif func.__name__ == "density":
        extension = "*.oef"

    dirname = os.path.join(system.name, f"compute-{system.compute_number-1}")
    output_file = max(
        glob.iglob(os.path.join(dirname, extension)), key=os.path.getctime
    )

    if func.__name__ == "energy":
        table = ut.Table.fromfile(output_file, rename=False)
        if isinstance(func.__self__, mm.Energy):
            col = [
                c for c in table.data.columns if c.endswith(":evolver:Total energy")
            ][0]
            output = table.data[col][0]
        else:
            output = table.data[
                f"{oxs_class(func.__self__, system)}:{func.__self__.name}:Energy"
            ][0]
    else:
        output = df.Field.fromfile(output_file)

    return output
