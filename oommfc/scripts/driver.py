import micromagneticmodel as mm
import ubermagutil.typesystem as ts

import oommfc as oc


def driver_script(driver, system, fixed_subregions=None, compute=None,
                  output_step=False, **kwargs):
    mif = ''
    if isinstance(driver, oc.HysteresisDriver):
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

        # Fixed spins
        if fixed_subregions is not None:
            resstr = f'{{main_atlas {" ".join(fixed_subregions)}}}'
            driver.evolver.fixed_spins = resstr

        mif += oc.scripts.evolver_script(driver.evolver)

        # Oxs_UZeeman
        Hmin, Hmax, n = kwargs['Hmin'], kwargs['Hmax'], kwargs['n']
        mif += '# OxS_UZeeman\n'
        mif += 'Specify Oxs_UZeeman:hysteresis {\n'
        mif += '  Hrange {\n'
        mif += '    {{ {} {} {} {} {} {} {} }}\n'.format(*Hmin, *Hmax, n - 1)
        mif += '    {{ {} {} {} {} {} {} {} }}\n'.format(*Hmax, *Hmin, n - 1)
        mif += '  }\n'
        mif += '}\n\n'

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

        # Fixed spins
        if fixed_subregions is not None:
            resstr = f'{{main_atlas {" ".join(fixed_subregions)}}}'
            driver.evolver.fixed_spins = resstr

        # What is saved in output?
        if output_step:
            output_str = 'Step'
        else:
            output_str = 'Stage'

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
        mif += f'Schedule DataTable table {output_str} 1\n'
        mif += f'Schedule Oxs_MinDriver::Magnetization mags {output_str} 1'

    if isinstance(driver, oc.TimeDriver):
        # Check evolver and set default if not passed.
        if driver.autoselect_evolver:
            if system.T > 0:
                msg = ('For simulations at finite temperature the evolver must'
                       'be specified explicitely.')
                raise RuntimeError(msg)
            elif mm.ZhangLi() in system.dynamics:
                driver.evolver = oc.SpinTEvolver()
            elif mm.Slonczewski() in system.dynamics:
                driver.evolver = oc.SpinXferEvolver()
            else:
                driver.evolver = oc.RungeKuttaEvolver()
        elif not isinstance(driver.evolver, (oc.EulerEvolver,
                                             oc.RungeKuttaEvolver,
                                             oc.SpinTEvolver,
                                             oc.SpinXferEvolver,
                                             oc.UHH_ThetaEvolver,
                                             oc.Xf_ThermHeunEvolver,
                                             oc.Xf_ThermSpinXferEvolver,
                                             )):
            msg = f'Cannot use {type(driver.evolver)} for evolver.'
            raise TypeError(msg)

        # Extract dynamics equation parameters.
        if mm.Precession() in system.dynamics:
            if isinstance(driver.evolver, oc.UHH_ThetaEvolver):
                pref = 1
                if mm.Damping() in system.dynamics:
                    pref += system.dynamics.damping.alpha**2
                driver.evolver.gamma_LL = (
                    system.dynamics.precession.gamma0 / pref)
                driver.evolver.do_precess = 1
            else:
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
            for arg in ['func', 'dt', 'tcl_strings']:
                if hasattr(system.dynamics.zhangli, arg):
                    setattr(driver.evolver, arg,
                            getattr(system.dynamics.zhangli, arg))
        if mm.Slonczewski() in system.dynamics:
            driver.evolver.J = system.dynamics.slonczewski.J
            driver.evolver.mp = system.dynamics.slonczewski.mp
            driver.evolver.P = system.dynamics.slonczewski.P
            driver.evolver.Lambda = system.dynamics.slonczewski.Lambda
            if isinstance(system.dynamics.slonczewski.eps_prime,
                          ts.Descriptor):
                driver.evolver.eps_prime = 0
            else:
                driver.evolver.eps_prime = \
                    system.dynamics.slonczewski.eps_prime
            for arg in ['func', 'dt', 'tcl_strings']:
                if (hasattr(system.dynamics.slonczewski, arg)
                        and not isinstance(
                            getattr(system.dynamics.slonczewski, arg),
                            ts.Descriptor)):
                    setattr(driver.evolver, arg,
                            getattr(system.dynamics.slonczewski, arg))
        if isinstance(driver.evolver, (oc.UHH_ThetaEvolver,
                                       oc.Xf_ThermHeunEvolver,
                                       oc.Xf_ThermSpinXferEvolver)):
            driver.evolver.temperature = system.T
        else:
            if system.T > 0:
                msg = (f'Evolver {driver.evolver} does not support finite'
                       ' temperature.')
                raise TypeError(msg)

        # Fixed spins
        if fixed_subregions is not None:
            resstr = f'{{main_atlas {" ".join(fixed_subregions)}}}'
            driver.evolver.fixed_spins = resstr

        mif += oc.scripts.evolver_script(driver.evolver, **kwargs)

        # Extract time and number of steps.
        t, n = kwargs['t'], kwargs['n']

        # TimeDriver
        mif += '# TimeDriver\n'
        mif += 'Specify Oxs_TimeDriver {\n'
        mif += '  evolver :evolver\n'
        mif += '  mesh :mesh\n'
        mif += '  Ms :m0_norm\n'
        mif += '  m0 :m0\n'
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
