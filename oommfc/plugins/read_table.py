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

    Examples
    --------
    1. Defining ``ubermagtable.Table`` by reading an OOMMF ``.odt`` file.

    >>> import os
    >>> from oommfc.plugins import table_from_file
    ...
    >>> odtfile = os.path.join(os.path.dirname(__file__), '..',
    ...                        'tests', 'test_sample', 'tables',
    ...                        'oommf-hysteresis1.odt')
    >>> table = table_from_file(odtfile, x='B_hysteresis')


    """
    with open(filename) as f:
        lines = f.readlines()

    cols = _columns(lines, rename=rename)
    units = _units(lines, cols)
    values = [
        list(map(float, line.split())) for line in lines if not line.startswith("#")
    ]
    return ubermagtable.Table(data=pd.DataFrame(values, columns=cols), units=units, x=x)


def _columns(lines, rename=True):
    """Extract column names from the lines of an OOMMF ``.odt`` file.

    The OOMMF class prefixes (e.g. ``Oxs_``) are always removed. If
    ``rename=True``, the column names are renamed with their shorter versions.
    """
    cline = next(line for line in lines if line.startswith("# Columns:"))
    cline = re.split(r"Oxs_|Anv_|Southampton_|My_|YY_|UHH_|Xf_", cline)[1:]
    cols = [re.sub(r"[{}]", "", col).strip() for col in cline]

    if rename:
        return [_rename_column(col, _OOMMF_DICT) for col in cols]
    return cols


def _units(lines, cols):
    """Map column names to the units from the lines of an OOMMF ``.odt`` file."""
    uline = next(line for line in lines if line.startswith("# Units:"))
    units = [re.sub(r"[{}]", "", unit) for unit in uline.split()[2:]]
    return dict(zip(cols, units))


def _rename_column(name, cols_dict):
    """Rename a column to a shorter name without spaces based on ``cols_dict``."""
    if name in cols_dict:
        return cols_dict[name]

    name_split = name.split(":")
    for key, type_name in cols_dict.items():
        if len(key.split("::")) == 2:
            start, end = key.split("::")
            if name_split[0] == start and name_split[-1] == end:
                term_name = name_split[1]
                # required for E_exchange in old and new OOMMF odt files
                if not type_name.endswith(term_name):
                    type_name = f"{type_name}_{term_name}"
                return type_name
    return name  # name cannot be found in dictionary


# The OOMMF columns (without class prefix) are renamed according to this dictionary.
_OOMMF_DICT = {
    "RungeKuttaEvolve:evolver:Total energy": "E",
    "RungeKuttaEvolve:evolver:Energy calc count": "E_calc_count",
    "RungeKuttaEvolve:evolver:Max dm/dt": "max_dm/dt",
    "RungeKuttaEvolve:evolver:dE/dt": "dE/dt",
    "RungeKuttaEvolve:evolver:Delta E": "delta_E",
    "RungeKuttaEvolve::Total energy": "E",
    "RungeKuttaEvolve::Energy calc count": "E_calc_count",
    "RungeKuttaEvolve::Max dm/dt": "max_dm/dt",
    "RungeKuttaEvolve::dE/dt": "dE/dt",
    "RungeKuttaEvolve::Delta E": "delta_E",
    "EulerEvolve:evolver:Total energy": "E",
    "EulerEvolve:evolver:Energy calc count": "E_calc_count",
    "EulerEvolve:evolver:Max dm/dt": "max_dmdt",
    "EulerEvolve:evolver:dE/dt": "dE/dt",
    "EulerEvolve:evolver:Delta E": "delta_E",
    "TimeDriver::Iteration": "iteration",
    "TimeDriver::Stage iteration": "stage_iteration",
    "TimeDriver::Stage": "stage",
    "TimeDriver::mx": "mx",
    "TimeDriver::my": "my",
    "TimeDriver::mz": "mz",
    "TimeDriver::Last time step": "last_time_step",
    "TimeDriver::Simulation time": "t",
    "CGEvolve:evolver:Max mxHxm": "max_mxHxm",
    "CGEvolve:evolver:Total energy": "E",
    "CGEvolve:evolver:Delta E": "delta_E",
    "CGEvolve:evolver:Bracket count": "bracket_count",
    "CGEvolve:evolver:Line min count": "line_min_count",
    "CGEvolve:evolver:Conjugate cycle count": "conjugate_cycle_count",
    "CGEvolve:evolver:Cycle count": "cycle_count",
    "CGEvolve:evolver:Cycle sub count": "cycle_sub_count",
    "CGEvolve:evolver:Energy calc count": "energy_calc_count",
    "CGEvolve::Max mxHxm": "max_mxHxm",
    "CGEvolve::Total energy": "E",
    "CGEvolve::Delta E": "delta_E",
    "CGEvolve::Bracket count": "bracket_count",
    "CGEvolve::Line min count": "line_min_count",
    "CGEvolve::Conjugate cycle count": "conjugate_cycle_count",
    "CGEvolve::Cycle count": "cycle_count",
    "CGEvolve::Cycle sub count": "cycle_sub_count",
    "CGEvolve::Energy calc count": "energy_calc_count",
    "FixedMEL::Energy": "MEL_E",
    "FixedMEL:magnetoelastic:Energy": "MEL_E",
    "SpinTEvolve:evolver:Total energy": "E",
    "SpinTEvolve:evolver:Energy calc count": "E_calc_count",
    "SpinTEvolve:evolver:Max dm/dt": "max_dmdt",
    "SpinTEvolve:evolver:dE/dt": "dE/dt",
    "SpinTEvolve:evolver:Delta E": "delta_E",
    "SpinTEvolve:evolver:average u": "average_u",
    "SpinXferEvolve:evolver:Total energy": "E",
    "SpinXferEvolve:evolver:Energy calc count": "E_calc_count",
    "SpinXferEvolve:evolver:Max dm/dt": "max_dmdt",
    "SpinXferEvolve:evolver:dE/dt": "dE/dt",
    "SpinXferEvolve:evolver:Delta E": "delta_E",
    "SpinXferEvolve:evolver:average u": "average_u",
    "SpinXferEvolve:evolver:average J": "average_J",
    "ThetaEvolve:evolver:Total energy": "E",
    "ThetaEvolve:evolver:Energy calc count": "E_calc_count",
    "ThetaEvolve:evolver:Max dm/dt": "max_dmdt",
    "ThetaEvolve:evolver:dE/dt": "dE/dt",
    "ThetaEvolve:evolver:Delta E": "delta_E",
    "ThetaEvolve:evolver:Temperature": "T",
    "ThermHeunEvolve:evolver:Total energy": "E",
    "ThermHeunEvolve:evolver:Energy calc count": "E_calc_count",
    "ThermHeunEvolve:evolver:Max dm/dt": "max_dmdt",
    "ThermHeunEvolve:evolver:dE/dt": "dE/dt",
    "ThermHeunEvolve:evolver:Delta E": "delta_E",
    "ThermHeunEvolve:evolver:Temperature": "T",
    "ThermSpinXferEvolve:evolver:Total energy": "E",
    "ThermSpinXferEvolve:evolver:Energy calc count": "E_calc_count",
    "ThermSpinXferEvolve:evolver:Max dm/dt": "max_dmdt",
    "ThermSpinXferEvolve:evolver:dE/dt": "dE/dt",
    "ThermSpinXferEvolve:evolver:Delta E": "delta_E",
    "ThermSpinXferEvolve:evolver:Temperature": "T",
    "MinDriver::Iteration": "iteration",
    "MinDriver::Stage iteration": "stage_iteration",
    "MinDriver::Stage": "stage",
    "MinDriver::mx": "mx",
    "MinDriver::my": "my",
    "MinDriver::mz": "mz",
    "UniformExchange::Max Spin Ang": "max_spin_ang",
    "UniformExchange::Stage Max Spin Ang": "stage_max_spin_ang",
    "UniformExchange::Run Max Spin Ang": "run_max_spin_ang",
    "UniformExchange::Energy": "E_exchange",
    "DMExchange6Ngbr::Energy": "E",
    "DMI_Cnv::Energy": "E",
    "DMI_T::Energy": "E",
    "DMI_D2d::Energy": "E",
    "Demag::Energy": "E",
    "FixedZeeman::Energy": "E_zeeman",
    "UZeeman::Energy": "E_zeeman",
    "UZeeman::B": "B",
    "UZeeman::Bx": "Bx",
    "UZeeman::By": "By",
    "UZeeman::Bz": "Bz",
    "ScriptUZeeman::Energy": "E",
    "ScriptUZeeman::B": "B",
    "ScriptUZeeman::Bx": "Bx",
    "ScriptUZeeman::By": "By",
    "ScriptUZeeman::Bz": "Bz",
    "TransformZeeman::Energy": "E",
    "CubicAnisotropy::Energy": "E",
    "UniaxialAnisotropy::Energy": "E",
    "UniaxialAnisotropy4::Energy": "E",
    "Southampton_UniaxialAnisotropy4::Energy": "E",
    "Exchange6Ngbr::Energy": "E",
    "Exchange6Ngbr::Max Spin Ang": "max_spin_ang",
    "Exchange6Ngbr::Stage Max Spin Ang": "stage_max_spin_ang",
    "Exchange6Ngbr::Run Max Spin Ang": "run_max_spin_ang",
    "ExchangePtwise::Energy": "E",
    "ExchangePtwise::Max Spin Ang": "max_spin_ang",
    "ExchangePtwise::Stage Max Spin Ang": "stage_max_spin_ang",
    "ExchangePtwise::Run Max Spin Ang": "run_max_spin_ang",
    "TwoSurfaceExchange::Energy": "E",
}
