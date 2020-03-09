import oommfc as oc
import micromagneticmodel as mm


def driver_script(driver, system, compute=None, **kwargs):
    mif = ''
    if isinstance(driver, oc.MinDriver):
        # Check evolver and set default if not passed.
        if not hasattr(driver, 'evolver'):
            driver.evolver = oc.CGEvolver()
        elif not isinstance(driver.evolver, oc.CGEvolver):
            msg = f'Cannot use {type(driver.evolver)} for evolver.'
            raise TypeError(msg)

        # Define default stopping_mxHxm if not passed. OOMMF cannot run without
        # this value.
        if not hasattr(driver, 'stopping_mxHxm'):
            driver.stopping_mxHxm = 0.1

        mif += oc.scripts.evolver_script(driver.evolver)

        # Minimisation driver script.
        mif += '# MinDriver\n'
        mif += 'Specify Oxs_MinDriver {\n'
        mif += '  evolver :evolver\n'
        mif += '  mesh :mesh\n'
        mif += '  Ms :m0_norm\n'
        mif += '  m0 :m0\n'
        for attr, value in driver:
            if attr != 'evolver':
                mif += f'  {attr} {value}\n'
        mif += '}\n\n'

        # Saving results.
        mif += 'Destination table mmArchive\n'
        mif += 'Destination mags mmArchive\n\n'
        mif += 'Schedule DataTable table Stage 1\n'
        mif += 'Schedule Oxs_MinDriver::Magnetization mags Stage 1'

    if isinstance(driver, oc.TimeDriver):
        # Check evolver and set default if not passed.
        if not hasattr(driver, 'evolver'):
            if mm.ZhangLi() in system.dynamics:
                driver.evolver = oc.SpinTEvolver()
            elif mm.Slonczewski() in system.dynamics:
                driver.evolver = oc.SpinXferEvolver()
            else:
                driver.evolver = oc.RungeKuttaEvolver()
        elif not isinstance(driver.evolver, (oc.EulerEvolver,
                                             oc.RungeKuttaEvolver,
                                             oc.SpinTEvolver,
                                             oc.SpinXferEvolver)):
            msg = f'Cannot use {type(driver.evolver)} for evolver.'
            raise TypeError(msg)

        # Extract dynamics equation parameters.
        if mm.Precession() in system.dynamics:
            driver.evolver.gamma_G = system.dynamics.precession.gamma0
        else:
            driver.evolver.do_precess = 0
        if mm.Damping() in system.dynamics:
            driver.evolver.alpha = system.dynamics.damping.alpha
        else:
            driver.evolver.alpha = 0
        if mm.ZhangLi() in system.dynamics:
            driver.evolver.u = system.dynamics.zhangli.u
            driver.evolver.beta = system.dynamics.zhangli.beta
        if mm.Slonczewski() in system.dynamics:
            driver.evolver.J = system.dynamics.slonczewski.J
            driver.evolver.mp = system.dynamics.slonczewski.mp
            driver.evolver.P = system.dynamics.slonczewski.P
            driver.evolver.Lambda = system.dynamics.slonczewski.Lambda
            driver.evolver.eps_prime = system.dynamics.slonczewski.eps_prime

        mif += oc.scripts.evolver_script(driver.evolver)

        # Extract time and number of steps.
        t, n = kwargs['t'], kwargs['n']

        # TimeDriver
        mif += '# TimeDriver\n'
        mif += 'Specify Oxs_TimeDriver {\n'
        mif += '  evolver :evolver\n'
        mif += '  mesh :mesh\n'
        mif += f'  Ms :m0_norm\n'
        mif += f'  m0 :m0\n'
        mif += f'  stopping_time {t/n}\n'
        mif += f'  stage_count {n}\n'
        for attr, value in driver:
            if attr != 'evolver':
                mif += f'  {attr} {value}\n'
        mif += '}\n\n'

        # Saving results
        mif += 'Destination table mmArchive\n'
        mif += 'Destination mags mmArchive\n'
        mif += 'Destination archive mmArchive\n\n'
        mif += 'Schedule DataTable table Stage 1\n'
        mif += 'Schedule Oxs_TimeDriver::Magnetization mags Stage 1\n'

        if compute is not None:
            mif += compute

    return mif
