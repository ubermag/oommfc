import oommfc as oc


def evolver_script(evolver):
    mif = ''

    # Prepare parameters depending on what attributes are defined in evolver.
    if hasattr(evolver, 'gamma_G'):
        gamma0mif, gamma0name = oc.scripts.setup_scalar_parameter(
            evolver.gamma_G, 'pr_gamma0')
        evolver.gamma_G = gamma0name
        mif += gamma0mif
    if hasattr(evolver, 'alpha'):
        alphamif, alphaname = oc.scripts.setup_scalar_parameter(
            evolver.alpha, 'dp_alpha')
        evolver.alpha = alphaname
        mif += alphamif
    if hasattr(evolver, 'u'):
        umif, uname = oc.scripts.setup_scalar_parameter(
            evolver.u, 'zl_alpha')
        evolver.u = uname
        mif += umif

    # Scripts for a specific evolver.
    if isinstance(evolver, oc.EulerEvolver):
        mif = '# EulerEvolver\n'
        mif += 'Specify Oxs_EulerEvolve:evolver {\n'
    elif isinstance(evolver, oc.RungeKuttaEvolver):
        mif += '# RungeKuttaEvolver\n'
        mif += 'Specify Oxs_RungeKuttaEvolve:evolver {\n'
    elif isinstance(evolver, oc.SpinTEvolver):
        mif += '# Zhang-Li evolver\n'
        mif += 'Specify Anv_SpinTEvolve:evolver {\n'
    elif isinstance(evolver, oc.CGEvolver):
        mif += '# CGEvolver\n'
        mif += 'Specify Oxs_CGEvolve:evolver {\n'

    # Define all other parameters.
    for attr, value in evolver:
        mif += f'  {attr} {value}\n'
    mif += '}\n\n'

    return mif
