import contextlib
import os
import re

import discretisedfield as df
import micromagneticmodel as mm
import ubermagtable as ut
import ubermagutil as uu

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

    return f'Schedule "{output}" archive Step 1\n'


def compute(
    func,
    system,
    /,
    dirname=".",
    append=True,
    n_threads=None,
    runner=None,
    ovf_format="bin8",
    verbose=1,
):
    """Computes a particular value of an energy term or energy container
    (``energy``, ``density``, or ``effective_field``).

    Parameters
    ----------
    func : callable

        A property of an energy term or an energy container.

    system : micromagneticmodel.System

        Micromagnetic system for which the property is calculated.

    dirname : str, optional

        Name of a base directory in which the simulation results are stored.
        Additional subdirectories based on the system name and the current drive
        number are created automatically. If not specified the current workinng
        directory is used.

    append : bool, optional

        If ``True`` and the system directory already exists, drive or
        compute directories will be appended. Defaults to ``True``.

    n_threads : int, optional

        Controls the number of threads that OOMMF uses. The number can alternatively
        also be controlled via the environment variable ``OOMMF_THREADS``. If not
        specified a default value that depends on the OOMMF installation (typically
        4) is used.

    ovf_format : str

        Format of the magnetisation output files written by OOMMF. Can be
        one of ``'bin8'`` (binary, double precision), ``'bin4'`` (binary,
        single precision) or ``'txt'`` (text-based, double precision).
        Defaults to ``'bin8'``.

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
    if system.T > 0:
        raise RuntimeError(
            "`oc.compute` does not support finite temperature."
            f" (Temperature is specified as {system.T=})"
        )

    td = oc.TimeDriver(total_iteration_limit=1)
    workingdir = td._setup_working_directory(
        system=system, dirname=dirname, mode="compute", append=append
    )
    with uu.changedir(workingdir):
        td.write_mif(
            system=system,
            t=1e-25,
            n=1,
            ovf_format=ovf_format,
            compute=schedule_script(func, system),
        )
        td._call(system=system, runner=runner, n_threads=n_threads, verbose=verbose)

    system.compute_number += 1

    if func.__name__ == "energy":
        extension = "odt"
    elif func.__name__ == "effective_field":
        extension = "ohf"
    elif func.__name__ == "density":
        extension = "oef"

    output_file = max(workingdir.glob(f"*.{extension}"), key=os.path.getctime)

    if func.__name__ == "energy":
        table = ut.Table.fromfile(output_file, rename=False)
        if isinstance(func.__self__, mm.Energy):
            col = [
                c for c in table.data.columns if c.endswith(":evolver:Total energy")
            ][0]
            output = table.data[col][0].item()
        else:
            output = table.data[
                f"{oxs_class(func.__self__, system)}:{func.__self__.name}:Energy"
            ][0].item()
    else:
        output = df.Field.from_file(output_file)
        with contextlib.suppress(FileNotFoundError):
            output.mesh.load_subregions(workingdir / "m0.omf")

    return output
