from ipywidgets import *
import textwrap
import base64
from IPython.display import Javascript, display
from IPython.utils.py3compat import str_to_bytes, bytes_to_str


def create_code_cell(code='', where='below'):
    """
    This function was written by jfreder and posted to GitHub here:
    https://github.com/ipython/ipython/issues/4983
    as a workaround to using set_next_input(some_text),
    as this does not work with widgets.
    """
    encoded_code = bytes_to_str(base64.b64encode(str_to_bytes(code)))
    display(Javascript("""
        var code = IPython.notebook.insert_cell_{0}('code');
        code.set_text(atob("{1}"));
    """.format(where, encoded_code)))


def GUI():
    a = _widget()
    return a.GUI


class _widget:

    def __init__(self):
        # Trying to keep MVC logic:
        # Functions provide logic to handle button presses, changing values
        # Only on click of "Generate code" style
        # These functions represent Control
        # The data model is a dictionary, which is updated by scanning through all widget property_dimension
        # which have name in the format property_*. Other functions are then called to assemble the
        # relevant Python code from the dictionary values.

        self.dict = {}

        # Functions which respond to changes made by the user while using the GUI.
        # These mostly disable/enable options which don't make sense otherwise.
        # e.g, if the user chooses a 1-D simulation, the properties that only
        # have relevance in 2-D or 3=D are disabled.

        # Note that these are defined in the init statement NOT as class functions, because
        # they can only take a single parameter, and if they are class functions, Python
        # automatically passes the parameter self. There is probably a way to work around
        # this but I've not had time to look into it.

        def on_dimension_change(b):
            if self.property_dimension.value == 1:
                self.property_Ly.layout.visibility = 'hidden'
                self.property_Lz.layout.visibility = 'hidden'
                self.property_dy.layout.visibility = 'hidden'
                self.property_dz.layout.visibility = 'hidden'
                self.property_initial_magnetisation.options = [
                    'Uniform', 'Neel Wall', 'Random']
                self.property_initial_magnetisation.value = 'Uniform'
                self.label_skyrmion_vortex_radius.layout.visibility = 'hidden'
                self.property_skyrmion_vortex_radius.layout.visibility = 'hidden'
            elif self.property_dimension.value == 2:
                self.property_Ly.layout.visibility = 'visible'
                self.property_Lz.layout.visibility = 'hidden'
                self.property_dy.layout.visibility = 'visible'
                self.property_dz.layout.visibility = 'hidden'
                self.property_initial_magnetisation.options = [
                    'Uniform', 'Neel Wall', 'Skyrmion', 'Vortex',  'Random']
                self.property_initial_magnetisation.value = 'Uniform'

            elif self.property_dimension.value == 3:
                self.property_Ly.layout.visibility = 'visible'
                self.property_Lz.layout.visibility = 'visible'
                self.property_dy.layout.visibility = 'visible'
                self.property_dz.layout.visibility = 'visible'
                self.property_initial_magnetisation.options = [
                    'Uniform', 'Neel Wall', 'Skyrmion', 'Vortex', 'Random']
                self.property_initial_magnetisation.value = 'Uniform'

        def on_change_anis(c):
            if not self.property_uniaxial_anisotropy_enabled.value:
                self.property_anisotropy_constant_K1.layout.visibility = 'hidden'
                self.property_anisotropy_axis.layout.visibility = 'hidden'
                self.label_anisotropy_constant_K1.layout.visibility = 'hidden'
            else:
                self.property_anisotropy_constant_K1.layout.visibility = 'visible'
                self.property_anisotropy_axis.layout.visibility = 'visible'
                self.label_anisotropy_constant_K1.layout.visibility = 'visible'

        def on_change_exch(c):
            if not self.property_exchange_enabled.value:
                self.property_exchange_constant.layout.visibility = 'hidden'
            else:
                self.property_exchange_constant.layout.visibility = 'visible'

        def on_change_simtype(c):
            if self.property_simtype.value == 'Relax':
                self.property_rununtil.layout.visibility = 'hidden'
                self.property_stopping_mxHxm.layout.visibility = 'visible'
            else:
                self.property_rununtil.layout.visibility = 'visible'
                self.property_stopping_mxHxm.layout.visibility = 'hidden'

        def normpress(c):
            r = np.sqrt(self.property_mx.value**2 + self.property_my.value**2 +
                        self.property_mz.value**2)
            self.property_mx.value /= r
            self.property_my.value /= r
            self.property_mz.value /= r

        def on_change_magnetisation_type(c):
            type = self.property_initial_magnetisation.value
            if type == 'Skyrmion' or type == 'Vortex':
                self.label_skyrmion_vortex_radius.layout.visibility = 'visible'
                self.label_domain_wall_width.layout.visibility = 'hidden'
                self.property_domain_wall_width.layout.visibility = 'hidden'
                self.property_skyrmion_vortex_radius.layout.visibility = 'visible'

            if type == 'Neel Wall' or type == 'Bloch Wall':
                self.label_skyrmion_vortex_radius.layout.visibility = 'hidden'
                self.label_domain_wall_width.layout.visibility = 'visible'
                self.property_domain_wall_width.layout.visibility = 'visible'
                self.property_skyrmion_vortex_radius.layout.visibility = 'hidden'

            if type == 'Uniform' or type == 'Random':
                self.label_skyrmion_vortex_radius.layout.visibility = 'hidden'
                self.label_domain_wall_width.layout.visibility = 'hidden'
                self.property_domain_wall_width.layout.visibility = 'hidden'
                self.property_skyrmion_vortex_radius.layout.visibility = 'hidden'

        def get_code(c):
            self.update_dictionary()
            self.code = 'import oommfc\nimport numpy as np\nimport finitedifferencefield\n'
            self.code += self.assemble_mesh_code()
            self.code += self.assemble_initial_magnetisation_code()
            self.code += self.assemble_interactions_code()
            self.code += self.assemble_properties_code()
            create_code_cell(self.code)

        # View:

        # Page 0 : Mesh Shape

        self.label_dimension = Label("Dimensions")
        self.property_dimension = IntSlider(value=1, min=1, max=3, step=1)
        self.label_lengths = Label("Mesh Lengths")
        self.property_Lx = IntText("10", description="Lx")
        self.property_Ly = IntText("1", description="Ly")
        self.property_Ly.layout.visibility = 'hidden'
        self.property_Lz = IntText("1", description="Lz")
        self.property_Lz.layout.visibility = 'hidden'
        self.label_scale = Label("Length Scale (m)")
        self.property_scale = FloatText(value=1e-9)
        self.label_discretisation = Label("Discretisation")
        self.property_dx = FloatText("1", description="dx")
        self.property_dy = FloatText("1", description="dy")
        self.property_dy.layout.visibility = 'hidden'
        self.property_dz = FloatText("1", description="dz")
        self.property_dz.layout.visibility = 'hidden'
        self.property_dimension.observe(on_dimension_change)
        self.label_periodicity = Label("Periodicity")
        self.property_periodic_x = Checkbox(description='x', value=False)
        self.property_periodic_y = Checkbox(description='y', value=False)
        self.property_periodic_z = Checkbox(description='z', value=False)

        self.page0 = widgets.Box((self.label_dimension, self.property_dimension,
                                  self.label_lengths, self.property_Lx,
                                  self.property_Ly, self.property_Lz,
                                  self.label_discretisation, self.property_dx,
                                  self.property_dy, self.property_dz,
                                  self.label_scale,
                                  self.property_scale,
                                  self.label_periodicity,
                                  self.property_periodic_x,
                                  self.property_periodic_y,
                                  self.property_periodic_z
                                  ))

        # Page 1 : Interactions

        self.label_Ms = Label("Saturation Magnetization (A/m)")
        self.property_Ms = FloatText(value=8e5, readout_format='.5e')
        self.box_Ms = Box([self.label_Ms, self.property_Ms])
        self.label_exchange = Label("Exchange (J/m)")
        self.property_exchange_enabled = Checkbox(
            value=True, description="Enabled")
        self.property_exchange_constant = FloatText(
            value=13e-12, readout_format='.5e')
        self.property_exchange_enabled.observe(on_change_exch)
        self.box_exchange = Box(
            [HBox([self.label_exchange, self.property_exchange_enabled]),
             self.property_exchange_constant])
        self.label_demagnetisation = Label("Demagnetisation")
        self.property_demagnetisation_enabled = Checkbox(
            value=False, description="Enabled")
        self.box_demagnetisation = HBox(
            [self.label_demagnetisation, self.property_demagnetisation_enabled])
        self.label_uniaxial_anisotropy = Label("Uniaxial Anisotropy")
        self.property_uniaxial_anisotropy_enabled = Checkbox(
            value=False, description="Enabled")
        self.label_anisotropy_constant_K1 = Label("K1 (J/m)")
        self.label_anisotropy_constant_K1.layout.visibility = 'hidden'
        self.property_anisotropy_constant_K1 = FloatText(value=1.3e-11)
        self.property_anisotropy_constant_K1.layout.visibility = 'hidden'
        self.property_anisotropy_axis = SelectMultiple(description="Axis",
                                                       options={
                                                           'x': 1, 'y': 2, 'z': 3})
        self.property_anisotropy_axis.layout.visibility = 'hidden'
        self.property_uniaxial_anisotropy_enabled.observe(on_change_anis)
        self.anisbox = Box([HBox([self.label_uniaxial_anisotropy, self.property_uniaxial_anisotropy_enabled]),
                            self.label_anisotropy_constant_K1, self.property_anisotropy_constant_K1,
                            self.property_anisotropy_axis])

        self.page1 = Box([self.box_Ms, self.box_exchange, self.box_demagnetisation,
                          self.anisbox])

        # Page 2 - Initial Magnetisation
        # Put this in later after  are working
        self.label_initial_magnetisation = Label("Initial magnetisation")
        self.property_initial_magnetisation = Dropdown(
            options=['Uniform', 'Neel Wall', 'Random'])
        self.box_initial_magnetisation = HBox(
            [self.label_initial_magnetisation, self.property_initial_magnetisation])
        self.label_skyrmion_vortex_radius = Label(
            "Skyrmion/Vortex Radius (nm)")
        self.property_skyrmion_vortex_radius = FloatText(value=10)
        self.label_domain_wall_width = Label("Wall width (nm)")
        self.property_domain_wall_width = FloatText(value=10)

        self.box_skyrmion_vortex_config = Box(
            [self.label_skyrmion_vortex_radius, self.property_skyrmion_vortex_radius])
        self.box_domain_wall_config = Box(
            [self.label_domain_wall_width, self.property_domain_wall_width])
        self.box_skyrmion_vortex_config.layout.visibility = 'hidden'
        self.box_domain_wall_config.layout.visibility = 'hidden'
        self.property_initial_magnetisation.observe(
            on_change_magnetisation_type)
        self.page2 = Box([self.box_initial_magnetisation,
                          self.box_domain_wall_config, self.box_skyrmion_vortex_config])

        # Page 3 : Simulation Parameters

        self.label_dt = Label("dt (s)")
        self.property_dt = FloatText(value=1e-9)

        self.property_stopping_mxHxm = FloatText(
            description="Stopping dmxHxm", value=0.01)
        self.property_saveevery = IntText(
            description="Save after every .. steps", value=100)
        self.property_maxsteps = IntText(description="Maximum number of steps")

        self.property_mx = FloatText(value=0.0)
        self.property_my = FloatText(value=0.0)
        self.property_mz = FloatText(value=0.0)
        self.norm = Button(description="Normalise m0")
        self.norm.on_click(normpress)
        self.label_simtype = Label("Simulation Type")
        self.property_simtype = RadioButtons(options=['Relax', 'Run until'])
        self.property_simtype.observe(on_change_simtype)
        self.property_rununtil = FloatText(value=10e-9)
        self.property_rununtil.layout.visibility = 'hidden'
        self.property_stopping_mxHxm = FloatText(value=0.01)
        self.get_code_button = Button(description="Generate Code")
        self.page3 = Box([HBox([self.label_dt, self.property_dt]),
                          self.property_saveevery, self.property_maxsteps,
                          self.label_simtype, self.property_simtype,
                          self.property_stopping_mxHxm,
                          self.property_rununtil])

        self.page4 = Box([self.get_code_button])

        self.get_code_button.on_click(get_code)

        # Header, assemble final layout

        self.maintitle = Label(
            "OOMMFC - A Python GUI for setting up OOMMF Simulations")
        self.maintitle.layout.padding = '10px'
        self.tabs = Accordion(
            [self.page0, self.page1, self.page2, self.page3, self.page4])
        self.tabs.set_title(0, 'Mesh')
        self.tabs.set_title(1, 'Interactions')
        self.tabs.set_title(2, 'Initial Magnetisation')
        self.tabs.set_title(3, 'Simulation Parameters')
        self.tabs.set_title(4, 'Generate Code')
        self.GUI = Box((self.maintitle, self.tabs))

    def update_dictionary(self):
        self.dict = {}
        internal_objects = dir(self)
        for item in internal_objects:
            if "property" in item:
                var = getattr(self, item)
                # Strip 'property' from left of name in assignment
                self.dict[item[9:]] = var.value

    def assemble_mesh_code(self):
        code = ""
        property_dimension = self.dict['dimension']
        dL = self.dict['scale']
        # We set these values to self as they are needed
        # in the assemble_initial_magnetisation_code,
        # and there's no point doing this twice.
        if property_dimension == 1:
            self.Lx = self.dict['Lx']*dL
            self.Ly = 1*dL
            self.Lz = 1*dL
            self.dx = self.dict['dx']*dL
            self.dy = 1*dL
            self.dz = 1*dL
        elif property_dimension == 2:
            self.Lx = self.dict['Lx']*dL
            self.Ly = self.dict['Ly']*dL
            self.Lz = 1*dL
            self.dx = self.dict['dx']*dL
            self.dy = self.dict['dy']*dL
            self.dz = 1*dL
        elif property_dimension == 3:
            self.Lx = self.dict['Lx']*dL
            self.Ly = self.dict['Ly']*dL
            self.Lz = self.dict['Lz']*dL
            self.dx = self.dict['dx']*dL
            self.dy = self.dict['dy']*dL
            self.dz = self.dict['dz']*dL
        property_Ms = self.dict['Ms']
        code = textwrap.dedent("""\

               atlas = oommfc.BoxAtlas((0, 0, 0), ({}, {}, {}))
               mesh = oommfc.RectangularMesh(atlas, ({}, {}, {}),
                                             periodicity=({}, {}, {}))

               sim = oommfc.Sim(mesh, {})

               """)

        return code.format(self.Lx, self.Ly, self.Lz,
                           self.dx, self.dy, self.dz,
                           1*self.dict['periodic_x'],
                           1*self.dict['periodic_y'],
                           1*self.dict['periodic_z'],
                           property_Ms
                           )

    def assemble_initial_magnetisation_code(self):
        type = self.dict['initial_magnetisation']
        code = ''
        if type == 'Uniform':
            code += textwrap.dedent("""

            def init_m(pos):
                return (0, 0, 1.0)

            """)
        elif type == 'Vortex':
            code += textwrap.dedent("""\

            def init_m(pos):
                x, y, z = pos
                xrad = 2*x - {}
                yrad = 2*y - {}
                sqrd = xrad*xrad + yrad*yrad
                if sqrd <= {}**2:
                    return (0.0, 0.0, 1.0)
                else:
                    return (yrad, -xrad, 0.0)


            """).format(self.Lx, self.Ly, self.dict['skyrmion_vortex_radius'])

        elif type == 'Skyrmion':
            code += textwrap.dedent("""\

			import scipy.optimize
			import numpy as np
			g = lambda x: -2 * np.sin(x)**2 - np.sin(2*x)/(2*x) + 1
			m_theta = lambda kr: np.sin(kr)
			m_z = lambda kr: -np.cos(kr)
			m_r = lambda kr: 0
			x0 = 3*np.pi/4
			kR = scipy.optimize.newton(g, x0)
			radius = 20
			k = kR/({}/2.)

			def init_m(pos):
			    x = 2*pos[0]-{}
			    y = 2*pos[1]-{}
			    r = (x**2 + y**2)**0.5
			    if r > radius*1.4:
			        return (0, 0, -1)
			    # Correction of arctan computation.
			    if x > 0:
			        theta = np.arctan(y/x)
			    elif x < 0:
			        theta = np.arctan(y/x) + np.pi
			    else:
			        if y > 0:
			            theta = np.pi/2
			        else:
			            theta = -np.pi/2
			    
			    m_x_init = -np.sin(theta) * m_theta(k*r)
			    m_y_init = np.cos(theta) * m_theta(k*r)
			    m_z_init = m_z(k*r)
			    return (m_x_init, m_y_init, m_z_init)

            """).format(self.dict['skyrmion_vortex_radius'], self.dict['Lx'], self.dict['Ly'])

        elif type == 'Random':
            code += textwrap.dedent("""\

            def init_m(pos):
                temp = np.random.uniform(-1, 1, 3)
                norm = np.linalg.norm(temp)
                return temp/norm
            """
                                    )

        elif type == 'Neel Wall':
            code += textwrap.dedent("""\

            def init_m(pos):
                x, y, z = pos
                wall_width = {}
                Lz = {}
                if z < (Lz - w)/2:
                    return (0, 0, 1)
                elif z >= (Lz-w)/2 and z <= (Lz + w)/2:
                    return (1, 1, 0)
                else:
                    return (0, 0, -1)

            """).format(self.dict['domain_wall_width'], self.dict['Lz'])

        dL = self.dict['scale']
        code += textwrap.dedent("""\

        field = finitedifferencefield.finitedifferencefield.Field((0, 0, 0),
                                                                  ({}, {}, {}),
                                                                  ({}, {}, {}),
                                                                  value=init_m)

        """).format(self.dict['Lx'], self.dict['Ly'], self.dict['Lz'],
                    self.dict['dx'], self.dict['dy'], self.dict['dz'])

        return code

    def assemble_interactions_code(self):
        code = ""
        axis = self.dict['anisotropy_axis']
        ax_x, ax_y, ax_z = 0, 0, 0
        if 1 in axis or axis == 1:
            ax_x = 1
        if 2 in axis or axis == 2:
            ax_y = 1
        if 3 in axis or axis == 3:
            ax_z = 1
        if self.dict['exchange_enabled']:
            code += textwrap.dedent("""\
                exchange = oommfc.energies.UniformExchange({})
                sim.add(exchange)
                """).format(self.dict['exchange_constant'])

        if self.dict['demagnetisation_enabled']:
            code += textwrap.dedent("""\

                demagnetisation = oommfc.energies.Demag()
                sim.add(demagnetisation)

                """)
        if self.dict['uniaxial_anisotropy_enabled']:
            code += textwrap.dedent("""\

                anis = oommfc.energies.UniaxialAnisotropy(K1={},
                                                        axis=({},{},{}))
                sim.add(anis)

                """).format(self.dict['anisotropy_constant_K1'],
                            ax_x, ax_y, ax_z)
        return code

    def assemble_properties_code(self):
        code = ""
        if self.dict['simtype'] == 'Relax':
            code += textwrap.dedent("""\
                sim.relax(stopping_mxHxm={})
                """).format(self.dict['stopping_mxHxm'])
        elif self.dict['simtype'] == 'Run until':
            code += textwrap.dedent("""\
                sim.run_until({}, {})
                """).format(self.dict['rununtil'], self.dict['saveevery'])
        return code
