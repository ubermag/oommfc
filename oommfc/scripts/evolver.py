import numbers

import numpy as np

import oommfc as oc


def evolver_script(evolver, **kwargs):
    mif = ""

    # Prepare parameters depending on what attributes are defined in evolver.
    if hasattr(evolver, "gamma_G"):
        gamma0mif, gamma0name = oc.scripts.setup_scalar_parameter(
            evolver.gamma_G, "pr_gamma0"
        )
        evolver.gamma_G = gamma0name
        mif += gamma0mif
    if hasattr(evolver, "alpha"):
        alphamif, alphaname = oc.scripts.setup_scalar_parameter(
            evolver.alpha, "dp_alpha"
        )
        evolver.alpha = alphaname
        mif += alphamif
    if hasattr(evolver, "u"):
        umif, uname = oc.scripts.setup_scalar_parameter(evolver.u, "zl_u")
        evolver.u = uname
        mif += umif

    # zhangli.beta cannot spatially vary - it has to be a constant.

    if hasattr(evolver, "J"):
        Jmif, Jname = oc.scripts.setup_scalar_parameter(evolver.J, "sl_J")
        evolver.J = Jname
        mif += Jmif
    if hasattr(evolver, "mp"):
        mpmif, mpname = oc.scripts.setup_vector_parameter(evolver.mp, "sl_mp")
        evolver.mp = mpname
        mif += mpmif
    if hasattr(evolver, "P"):
        Pmif, Pname = oc.scripts.setup_scalar_parameter(evolver.P, "sl_P")
        evolver.P = Pname
        mif += Pmif
    if hasattr(evolver, "Lambda"):
        Lambda = evolver.Lambda
        if isinstance(evolver.Lambda, dict):
            # the automatically added default value 0 is not allowed
            Lambda = evolver.Lambda.copy()
            if "default" not in Lambda:
                Lambda["default"] = 1
        Lambdamif, Lambdaname = oc.scripts.setup_scalar_parameter(Lambda, "sl_Lambda")
        evolver.Lambda = Lambdaname
        mif += Lambdamif
    if hasattr(evolver, "eps_prime"):
        eps_primemif, eps_primename = oc.scripts.setup_scalar_parameter(
            evolver.eps_prime, "sl_eps_prime"
        )
        evolver.eps_prime = eps_primename
        mif += eps_primemif

    if hasattr(evolver, "dt") and isinstance(evolver.dt, numbers.Real):
        ts = np.arange(0, kwargs["t"] + evolver.dt, evolver.dt)
        tlist = [evolver.func(t) for t in ts]

        mif += "proc TimeFunction { total_time } {\n"
        mif += f"  set tstep {evolver.dt}\n"
        mif += "  set index [expr round($total_time/$tstep)]\n"
        mif += f'  set profile {{ {" ".join(map(str, tlist))} }}\n'
        mif += "  set factor [lindex $profile $index]\n"
        mif += "  return $factor\n"
        mif += "}\n\n"

        if isinstance(evolver, (oc.SpinXferEvolver)):
            # oc.Xf_TherrmSpinXferEvolver)):
            setattr(evolver, "J_profile", "TimeFunction")
            setattr(evolver, "J_profile_args", "total_time")
        elif isinstance(evolver, oc.SpinTEvolver):
            setattr(evolver, "u_profile", "TimeFunction")
            setattr(evolver, "u_profile_args", "total_time")
    if hasattr(evolver, "tcl_strings") and isinstance(evolver.tcl_strings, dict):
        print(evolver.tcl_strings)
        mif += evolver.tcl_strings["script"]
        if isinstance(evolver, (oc.SpinXferEvolver)):
            # oc.Xf_ThermSpinXferEvolver)):
            setattr(evolver, "J_profile", evolver.tcl_strings["script_name"])
            setattr(evolver, "J_profile_args", evolver.tcl_strings["script_args"])
        elif isinstance(evolver, oc.SpinTEvolver):
            setattr(evolver, "u_profile", evolver.tcl_strings["script_name"])
            setattr(evolver, "u_profile_args", evolver.tcl_strings["script_args"])

    # temperature cannot spacially vary

    # Scripts for a specific evolver.
    if isinstance(evolver, oc.EulerEvolver):
        mif += "# EulerEvolver\n"
        mif += "Specify Oxs_EulerEvolve:evolver {\n"
    elif isinstance(evolver, oc.RungeKuttaEvolver):
        mif += "# RungeKuttaEvolver\n"
        mif += "Specify Oxs_RungeKuttaEvolve:evolver {\n"
    elif isinstance(evolver, oc.SpinTEvolver):
        # time dependence
        mif += "# Zhang-Li evolver\n"
        mif += "Specify Anv_SpinTEvolve:evolver {\n"
    elif isinstance(evolver, oc.SpinXferEvolver):
        # time dependence
        mif += "# Slonczewski evolver\n"
        mif += "Specify Oxs_SpinXferEvolve:evolver {\n"
    elif isinstance(evolver, oc.CGEvolver):
        mif += "# CGEvolver\n"
        mif += "Specify Oxs_CGEvolve:evolver {\n"
    elif isinstance(evolver, oc.UHH_ThetaEvolver):
        mif += "# UHH_ThetaEvolver\n"
        mif += "Specify UHH_ThetaEvolve:evolver {\n"
    elif isinstance(evolver, oc.Xf_ThermHeunEvolver):
        mif += "# Xf_ThermHeunEvolver\n"
        mif += "Specify Xf_ThermHeunEvolve:evolver {\n"
    elif isinstance(evolver, oc.Xf_ThermSpinXferEvolver):
        mif += "# Xf_ThermSpinXferEvolver\n"
        mif += "Specify Xf_ThermSpinXferEvolve:evolver {\n"

    # Define all other parameters.
    for attr, value in evolver:
        if attr not in ["time_dependence", "tstep", "tcl_strings"]:
            mif += f"  {attr} {value}\n"
    mif += "}\n\n"

    return mif
