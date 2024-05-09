import re

import pandas as pd
import ubermagtable


def table_from_file(filename, /, x=None, rename=True):
    """Convert an OOMMF ``.odt`` scalar data file into a ``ubermagtable.Table``.

    Parameters
    ----------
    filename : str

        OOMMF ``.odt`` file.

    x : str, optional

        Independent variable name. Defaults to ``None``.

    rename : bool, optional

        If ``rename=True``, the column names are renamed with their shorter
        versions. Defaults to ``True``.

    Returns
    -------
    ubermagtable.Table

        Table object.

    TODO: update example
    Examples
    --------
    1. Defining ``ubermagtable.Table`` by reading an OOMMF ``.odt`` file.

    >>> import os
    >>> import ubermagtable as ut
    ...
    >>> odtfile = os.path.join(os.path.dirname(__file__),
    ...                        'tests', 'test_sample',
    ...                        'oommf-hysteresis1.odt')
    >>> table = ut.Table.fromfile(odtfile, x='B_hysteresis')

    2. Defining ``ubermagtable.Table`` by reading a mumax3 ``.txt`` file.

    >>> odtfile = os.path.join(os.path.dirname(__file__),
    ...                        'tests', 'test_sample', 'mumax3-file1.txt')
    >>> table = ut.Table.fromfile(odtfile, x='t')

    """
    quantities = _read_header(filename, rename=rename)
    data = pd.read_csv(
        filename,
        sep=r"\s+",
        comment="#",
        header=None,
        names=list(quantities.keys()),
    )
    return ubermagtable.Table(data=data, units=quantities, x=x)


def _read_header(filename, rename=True):
    """Extract quantities for individual columns from a table file.

    This method extracts both column names and units and returns a dictionary,
    where keys are column names and values are the units.

    Parameters
    ----------
    filename : str

        OOMMF ``.odt`` file.

    rename : bool

        If ``rename=True``, the column names are renamed with their shorter
        versions. Defaults to ``True``.

    Returns
    -------
    dict

        Dictionary of column names and units.
    """
    with open(filename) as f:
        # COLUMN NAMES
        while not (cline := f.readline()).startswith("# Columns"):
            pass
        columns = cline.lstrip("# Columns:").rstrip()
        # Columns can e.g. look like:
        # {Oxs_CGEvolve:evolver:Max mxHxm} {...} Oxs_MinDriver::Stage Oxs_MinDriver::mx
        # - the first part of the regex finds column names with spaces inside {}
        # - the second part finds column names without spaces and without {}
        cols = re.findall(r"(?<={)[^}]+|[^ {}]+", columns)
        # UNITS
        uline = f.readline()
        assert uline.startswith("# Units:")
        units = uline.split()[2:]  # [2:] to remove ["#", "Units:"]
        units = [re.sub(r"[{}]", "", unit) for unit in units]

    if rename:
        cols = [_rename_column(col, _OOMMF_DICT) for col in cols]

    return dict(zip(cols, units))


def _rename_column(name, cols_dict):
    """Rename columns to get shorter names without spaces.

    Renaming is based on _OOMMF_DICT.
    """
    name_split = name.split(":")
    try:
        group = cols_dict[name_split[0]]
        attribute = group[name_split[-1]]
        term_name = name_split[1]
        if not attribute.endswith(term_name):
            # - unique names if the same quantity is present multiple times
            #   e.g. multiple Zeeman fields
            # - also required for changes in the exchange field in "old" and "new"
            #   OOMMF odt files
            attribute = f"{attribute}_{term_name}"
        return attribute
    except KeyError:
        return name


# The OOMMF columns are renamed according to this dictionary.
_OOMMF_DICT = {
    "Oxs_RungeKuttaEvolve": {
        "Total energy": "E",
        "Energy calc count": "E_calc_count",
        "Max dm/dt": "max_dm/dt",
        "dE/dt": "dE/dt",
        "Delta E": "delta_E",
    },
    "Oxs_EulerEvolve": {
        "Total energy": "E",
        "Energy calc count": "E_calc_count",
        "Max dm/dt": "max_dmdt",
        "dE/dt": "dE/dt",
        "Delta E": "delta_E",
    },
    "Oxs_CGEvolve": {
        "Max mxHxm": "max_mxHxm",
        "Total energy": "E",
        "Delta E": "delta_E",
        "Bracket count": "bracket_count",
        "Line min count": "line_min_count",
        "Conjugate cycle count": "conjugate_cycle_count",
        "Cycle count": "cycle_count",
        "Cycle sub count": "cycle_sub_count",
        "Energy calc count": "energy_calc_count",
    },
    "Anv_SpinTEvolve": {
        "Total energy": "E",
        "Energy calc count": "E_calc_count",
        "Max dm/dt": "max_dmdt",
        "dE/dt": "dE/dt",
        "Delta E": "delta_E",
        "average u": "average_u",
    },
    "Oxs_SpinXferEvolve": {
        "Total energy": "E",  # NO SAMPLE
        "Energy calc count": "E_calc_count",  # NO SAMPLE
        "Max dm/dt": "max_dmdt",  # NO SAMPLE
        "dE/dt": "dE/dt",  # NO SAMPLE
        "Delta E": "delta_E",  # NO SAMPLE
        "average u": "average_u",  # NO SAMPLE
        "average J": "average_J",  # NO SAMPLE
    },
    "UHH_ThetaEvolve": {
        "Total energy": "E",  # NO SAMPLE
        "Energy calc count": "E_calc_count",  # NO SAMPLE
        "Max dm/dt": "max_dmdt",  # NO SAMPLE
        "dE/dt": "dE/dt",  # NO SAMPLE
        "Delta E": "delta_E",  # NO SAMPLE
        "Temperature": "T",  # NO SAMPLE
    },
    "Xf_ThermHeunEvolve": {
        "Total energy": "E",  # NO SAMPLE
        "Energy calc count": "E_calc_count",  # NO SAMPLE
        "Max dm/dt": "max_dmdt",  # NO SAMPLE
        "dE/dt": "dE/dt",  # NO SAMPLE
        "Delta E": "delta_E",  # NO SAMPLE
        "Temperature": "T",  # NO SAMPLE
    },
    "Xf_ThermSpinXferEvolve": {
        "Total energy": "E",  # NO SAMPLE
        "Energy calc count": "E_calc_count",  # NO SAMPLE
        "Max dm/dt": "max_dmdt",  # NO SAMPLE
        "dE/dt": "dE/dt",  # NO SAMPLE
        "Delta E": "delta_E",  # NO SAMPLE
        "Temperature": "T",  # NO SAMPLE
    },
    "Oxs_MinDriver": {
        "Iteration": "iteration",
        "Stage iteration": "stage_iteration",
        "Stage": "stage",
        "mx": "mx",
        "my": "my",
        "mz": "mz",
    },
    "Oxs_TimeDriver": {
        "Iteration": "iteration",
        "Stage iteration": "stage_iteration",
        "Stage": "stage",
        "mx": "mx",
        "my": "my",
        "mz": "mz",
        "Last time step": "last_time_step",
        "Simulation time": "t",
    },
    "Oxs_UniformExchange": {
        "Max Spin Ang": "max_spin_ang",
        "Stage Max Spin Ang": "stage_max_spin_ang",
        "Run Max Spin Ang": "run_max_spin_ang",
        "Energy": "E_exchange",
    },
    "Oxs_Exchange6Ngbr": {
        "Energy": "E_exchange6ngbr",
        "Max Spin Ang": "max_spin_ang",
        "Stage Max Spin Ang": "stage_max_spin_ang",
        "Run Max Spin Ang": "run_max_spin_ang",
    },
    "Oxs_ExchangePtwise": {
        "Energy": "E_exchange_ptwise",  # NO SAMPLE
        "Max Spin Ang": "max_spin_ang",  # NO SAMPLE
        "Stage Max Spin Ang": "stage_max_spin_ang",  # NO SAMPLE
        "Run Max Spin Ang": "run_max_spin_ang",  # NO SAMPLE
    },
    "Oxs_TwoSurfaceExchange": {"Energy": "E_two_surface_exchange"},  # NO SAMPLE
    "Oxs_Demag": {"Energy": "E_demag"},
    "Oxs_DMExchange6Ngbr": {"Energy": "E_DM_exchange6ngbr"},  # NO SAMPLE
    "Oxs_DMI_Cnv": {"Energy": "E_DMI_Cnv"},  # TODO: PREFIX
    "Oxs_DMI_T": {"Energy": "E_DMI_T"},  # NO SAMPLE,  TODO: PREFIX
    "Oxs_DMI_D2d": {"Energy": "E_DMI_Dd"},  # NO SAMPLE,  TODO: PREFIX
    "Oxs_FixedZeeman": {"Energy": "E_zeeman"},
    "Oxs_UZeeman": {
        "Energy": "E_zeeman",
        "B": "B",
        "Bx": "Bx",
        "By": "By",
        "Bz": "Bz",
    },
    "Oxs_ScriptUZeeman": {
        "Energy": "E_zeeman",  # NO SAMPLE
        "B": "B",  # NO SAMPLE
        "Bx": "Bx",  # NO SAMPLE
        "By": "By",  # NO SAMPLE
        "Bz": "Bz",  # NO SAMPLE
    },
    "Oxs_TransformZeeman": {"Energy": "E_zeeman"},  # NO SAMPLE
    "Oxs_CubicAnisotropy": {"Energy": "E_zeeman"},
    "Oxs_UniaxialAnisotropy": {"Energy": "E_zeeman"},
    "Southampton_UniaxialAnisotropy4": {"Energy": "E_zeeman"},  # NO SAMPLE
    "YY_FixedMEL": {"Energy": "MEL_E"},
}
