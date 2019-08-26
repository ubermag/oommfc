import oommfc as oc
import oommfc.util as ou
from .driver import Driver


class TimeDriver(Driver):
    """Time driver.

    This class is used for collecting additional parameters, which
    could be passed to `Oxs_TimeDriver`. Only parameters which are
    defined in `_allowed_kwargs` can be passed.

    Examples
    --------
    1. Defining driver

    >>> import oommfc as oc
    ...
    >>> td = oc.TimeDriver()

    2. Passing an argument which is not allowed

    >>> import oommfc as oc
    ...
    >>> td = oc.TimeDriver(myarg=3)
    Traceback (most recent call last):
       ...
    AttributeError: ...

    """
    _allowed_kwargs = ['evolver',
                       'stopping_dm_dt',
                       'stage_iteration_limit',
                       'total_iteration_limit',
                       'stage_count_check',
                       'checkpoint_file',
                       'checkpoint_interval',
                       'checkpoint_disposal',
                       'start_iteration',
                       'start_stage',
                       'start_stage_iteration',
                       'start_stage_start_time',
                       'start_stage_elapsed_time',
                       'start_last_timestep',
                       'normalize_aveM_output',
                       'report_max_spin_angle',
                       'report_wall_time']

    def _script(self, system, **kwargs):
        # Save initial magnetisation.
        m0mif, m0name, Msname = ou.setup_m0(system.m, 'm0')
        mif = m0mif

        # Extract dynamics equation parameters.
        gamma, alpha, u, beta = None, None, None, None
        for term in system.dynamics.terms:
            if isinstance(term, oc.Precession):
                gamma = term.gamma
            if isinstance(term, oc.Damping):
                alpha = term.alpha
            if isinstance(term, oc.ZhangLi):
                u = term.u
                beta = term.beta

        # Evolver
        if not hasattr(self, 'evolver'):
            if u is not None:
                self.evolver = oc.SpinTEvolver()
            else:
                self.evolver = oc.RungeKuttaEvolver()

        if gamma is not None:
            self.evolver.gamma_G = gamma
        else:
            self.evolver.do_precess = 0  # do_precess default value is 1

        if alpha is not None:
            self.evolver.alpha = alpha
        else:
            self.evolver.alpha = 0

        if u is not None:
            self.evolver.u = u
        if beta is not None:
            self.evolver.beta = beta

        # Evolver script
        if isinstance(self.evolver, (oc.EulerEvolver, oc.RungeKuttaEvolver,
                                     oc.SpinTEvolver)):
            mif += self.evolver._script
        else:
            msg = ('Evolver must be either EulerEvolver, '
                   'RungeKuttaEvolver, or SpinTEvolver')
            raise ValueError(msg)

        # For deriving, a small timestep is chosen.
        if 'derive' in kwargs:
            t, n = 1e-25, 1
            self.total_iteration_limit = 1
        else:
            t, n = kwargs['t'], kwargs['n']

        # TimeDriver
        mif += '# TimeDriver\n'
        mif += 'Specify Oxs_TimeDriver {\n'
        mif += '  evolver :evolver\n'
        mif += '  mesh :mesh\n'
        mif += f'  Ms :{Msname}\n'
        mif += f'  m0 :{m0name}\n'
        mif += f'  stopping_time {t/n}\n'
        mif += f'  stage_count {n}\n'
        # Other parameters for TimeDriver
        for kwarg in self._allowed_kwargs:
            if hasattr(self, kwarg) and kwarg != 'evolver':
                mif += f'  {kwarg} {getattr(self, kwarg)}\n'
        mif += '}\n\n'

        # Saving results
        mif += 'Destination table mmArchive\n'
        mif += 'Destination mags mmArchive\n'
        mif += 'Destination archive mmArchive\n\n'

        if 'derive' in kwargs:
            if 'ield' in kwargs['derive'] or 'density' in kwargs['derive']:
                mif += ('Schedule \"{}\" archive '
                        'Step 1'.format(kwargs['derive']))
            else:
                mif += 'Schedule DataTable table Stage 1\n'
        else:
            mif += 'Schedule DataTable table Stage 1\n'
            mif += 'Schedule Oxs_TimeDriver::Magnetization mags Stage 1'

        return mif

    def _checkargs(self, **kwargs):
        if 'derive' not in kwargs:
            if kwargs['t'] <= 0:
                msg = 'Positive simulation time expected (t>0).'
                raise ValueError(msg)
            if kwargs['n'] <= 0 or not isinstance(kwargs['n'], int):
                msg = 'Positive integer number of steps expected (n>0)'
                raise ValueError(msg)
