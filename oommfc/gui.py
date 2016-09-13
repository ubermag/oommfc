from ipywidgets import *
import textwrap


def GUI():
    # try:
    a = _widget()
    return a.GUI
    # except:
    #    print("This must be called within a Jupyter Notebook.\n"
    #
    #          "Requires IPython >= 4.2 and ipywidgets >= 5")


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

        def on_dimension_change(b):
            if self.property_dimension.value == 1:
                self.property_Ly.disabled = True
                self.property_Lz.disabled = True
                self.property_dy.disabled = True
                self.property_dz.disabled = True
                self.property_initial_magnetisation.options  = ['Uniform', 'Neel Wall', 'Random']
                self.property_initial_magnetisation.value = 'Uniform'
                self.property_skyrmion_vortex_radius.visible = False
            elif self.property_dimension.value == 2:
                self.property_Ly.disabled = False
                self.property_Lz.disabled = True
                self.property_dy.disabled = False
                self.property_dz.disabled = True
                self.property_initial_magnetisation.options  = ['Uniform', 'Neel Wall', 'Skyrmion', 'Vortex',  'Random']
                self.property_initial_magnetisation.value = 'Uniform'
            elif self.property_dimension.value == 3:
                self.property_Ly.disabled = False
                self.property_Lz.disabled = False
                self.property_dy.disabled = False
                self.property_dz.disabled = False
                self.property_initial_magnetisation.options  = ['Uniform', 'Neel Wall', 'Skyrmion', 'Vortex', 'Random']
                self.property_initial_magnetisation.value = 'Uniform'

        def on_change_anis(c):
            if not self.property_anis_enabled.value:
                self.property_anisotropy_constant_K1.disabled = True
                self.property_anisotropy_axis.disabled = True
            else:
                self.property_anisotropy_constant_K1 = False
                self.property_anisotropy_axis.disabled = False

        def on_change_exch(c):
            if not self.property_exchange_enabled.value:
                self.property_exchange_constant.disabled = True
            else:
                self.property_exchange_constant.disabled = False


        def on_change_simtype(c):
            if self.property_simtype.value == 'Relax':
                self.property_rununtil.disabled = True
                self.property_stopping_mxHxm.disabled = False
            else:
                self.property_rununtil.disabled = False
                self.property_stopping_mxHxm.disabled = True

        def normpress(c):
            r = np.sqrt(self.property_mx.value**2 + self.property_my.value**2 +
                        self.property_mz.value**2)
            self.property_mx.value /= r
            self.property_my.value /= r
            self.property_mz.value /= r

        def on_change_magnetisation_type(c):
            type = self.property_initial_magnetisation.value
            print(type)
            if type == 'Skyrmion' or type == 'Vortex':
                print('a')
                self.property_domain_wall_width.disabled = True
                self.property_skyrmion_vortex_radius.disabled = False
            if type == 'Neel Wall' or type == 'Bloch Wall':
                print('b')
                self.property_domain_wall_width.disabled = False
                self.property_skyrmion_vortex_radius.disabled = True

            if type == 'Uniform' or type == 'Random':
                print('b')
                self.property_domain_wall_width.disabled = True
                self.property_skyrmion_vortex_radius.disabled = True

        def on_click_getcode(c):
            self.code_output.value = "import oommfc\n"

        def update_dictionary():
            self.dict = {}
            internal_objects = dir(self)
            for item in internal_objects:
                if "property" in item:
                    var = getattr(self, item)
                    self.dict[item[9:]] = var.value

        def get_code(c):
            update_dictionary()
            code = 'import oommfc\nimport numpy\n'

            code += assemble_initial_magnetisation_code()

            code += assemble_mesh_code()
            code += assemble_interactions_code()
            code += assemble_properties_code()
            self.code_output.value = code

        def assemble_mesh_code():
            update_dictionary()
            code = ""
            property_dimension = self.dict['dimension']
            dL = self.dict['scale']
            if property_dimension == 1:
               property_Lx = self.dict['Lx']*dL
               property_Ly = 1*dL
               property_Lz = 1*dL
               property_dx = self.dict['dx']*dL
               property_dy = 1*dL
               property_dz = 1*dL
            elif property_dimension == 2:
                property_Lx = self.dict['Lx']*dL
                property_Ly = self.dict['Ly']*dL
                property_Lz = 1*dL
                property_dx = self.dict['dx']*dL
                property_dy = self.dict['dy']*dL
                property_dz = 1*dL
            elif property_dimension == 3:
                property_Lx = self.dict['Lx']*dL
                property_Ly = self.dict['Ly']*dL
                property_Lz = self.dict['Lz']*dL
                property_dx = self.dict['dx']*dL
                property_dy = self.dict['dy']*dL
                property_dz = self.dict['dz']*dL
            property_Ms = self.dict['Ms']
            code = textwrap.dedent("""\

                   atlas = oommfc.BoxAtlas((0, 0, 0), ({}, {}, {}))
                   mesh = oommfc.RectangularMesh(atlas, ({}, {}, {}))
                   sim = oommfc.Sim(mesh, {})
                   sim.set_m(init_m)
                   """)

            return code.format(property_Lx, property_Ly, property_Lz,
                               property_dx, property_dy, property_dz,
                               property_Ms)


        def assemble_initial_magnetisation_code():
            code = "import finitedifferencefield\n"
            type = self.dict['initial_magnetisation']
            if type == 'uniform':
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


                """).format(self.dict['Lx'], self.dict['Ly'], self.dict['skyrmion_vortex_radius'])

            elif type == 'Skyrmion':
                code += textwrap.dedent("""\
                import scipy.optimize

                g = lambda x: -2 * np.sin(x)**2 - np.sin(2*x)/(2*x) + 1
                m_theta = lambda kr: np.sin(kr)
                m_z = lambda kr: -np.cos(kr)
                m_r = lambda kr: 0

                x0 = 3*np.pi/4
                kR = scipy.optimize.newton(g, x0)
                k = kR/(d/2.)

                def m_init(pos):
                    x = 2*{} - {}
                    y = 2*{} - {}
                    r = (x**2 + y**2)**0.5

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

                """).format(self.dict['Lx'], self.dict['Ly'], self.dict['skyrmion_vortex_radius'])

            elif type == 'Uniform':
                code += textwrap.dedent("""\
                init_m = lambda pos: (0, 0, 1)
                """)

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
                """).format(self.dict['wall_width'], self.dict['Lz'])


            code += textwrap.dedent("""\
            field = finitedifferencefield.finitedifferencefield.Field((0, 0, 0),
                                                                      ({}, {}, {}),
                                                                      ({}, {}, {}),
                                                                      value=init_m)
            """).format(self.dict['Lx'], self.dict['Ly'], self.dict['Lz'],
                        self.dict['dx'], self.dict['dy'], self.dict['dz'])

            return code











        def assemble_interactions_code():
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

                    anis = oommfc.energies.UniaxialAnisotropy(Ku={},
                                                            axis=({},{},{}))
                    sim.add(anis)

                    """).format(self.dict['anisotropy_constant_K1'],
                                ax_x, ax_y, ax_z)
            return code

        def assemble_properties_code():
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



        # View:

        # Page 0 : Mesh Shape

        self.label_dimension = Label("Dimensions")
        self.property_dimension = IntSlider(value=1, min=1, max=3, step=1)
        self.label_lengths = Label("Mesh Lengths")
        self.property_Lx = IntText("10", description="Lx")
        self.property_Ly = IntText("1", description="Ly", disabled=True)
        self.property_Lz = IntText("1", description="Lz", disabled=True)
        self.label_scale = Label("Length Scale (m)")
        self.property_scale = FloatText(value=1e-9)
        self.label_discretisation = Label("Discretisation")
        self.property_dx = FloatText("1", description="dx")
        self.property_dy = FloatText("1", description="dy", disabled=True)
        self.property_dz = FloatText("1", description="dz", disabled=True)

        self.property_dimension.observe(on_dimension_change)
        self.page0 = widgets.Box((self.label_dimension, self.property_dimension,
                                  self.label_lengths, self.property_Lx,
                                  self.property_Ly, self.property_Lz,
                                  self.label_discretisation, self.property_dx,
                                  self.property_dy, self.property_dz,
                                  self.label_scale,
                                  self.property_scale,
                                  ))

        # Page 1 : Interactions

        self.label_Ms = Label("Saturation Magnetization (A/m)")
        self.property_Ms = FloatText(value=8e5, readout_format='.5e')
        self.box_Ms = Box([self.label_Ms, self.property_Ms])
        self.label_exchange = Label("Exchange (J/m)")
        self.property_exchange_enabled = Checkbox(
            value=True, description="Enabled")
        self.property_exchange_constant = FloatText(value=13e-12, readout_format='.5e')
        self.property_exchange_enabled.observe(on_change_exch)
        self.box_exchange = Box(
            [HBox([self.label_exchange, self.property_exchange_enabled]),
             self.property_exchange_constant])
        self.label_demagnetisation = Label("Demagnetisation")
        self.property_demagnetisation_enabled = Checkbox(
            value=False, description="Enabled")
        self.box_demagnetisation = HBox([self.label_demagnetisation, self.property_demagnetisation_enabled])
        self.label_uniaxial_anisotropy = Label("Uniaxial Anisotropy")
        self.property_uniaxial_anisotropy_enabled = Checkbox(
            value=False, description="Enabled")
        self.property_anisotropy_constant_K1 = FloatText(value=1.3e-11, disabled=True)
        self.property_anisotropy_axis = SelectMultiple(description="Axis",
                                                       options={
                                                       'x': 1, 'y': 2, 'z': 3},
                                                       disabled=True)
        self.property_uniaxial_anisotropy_enabled.observe(on_change_anis)
        self.anisbox = Box([HBox([self.label_uniaxial_anisotropy, self.property_uniaxial_anisotropy_enabled]),
                            self.property_anisotropy_constant_K1, self.property_anisotropy_axis])

        self.page1 = Box([self.box_Ms, self.box_exchange, self.box_demagnetisation,
                          self.anisbox])

        # Page 2 - Initial Magnetisation
        # Put this in later after  are working
        self.label_initial_magnetisation = Label("Initial magnetisation")
        self.property_initial_magnetisation = Dropdown(options=['Uniform', 'Neel Wall', 'Random'])
        self.box_initial_magnetisation = HBox([self.label_initial_magnetisation, self.property_initial_magnetisation])
        self.label_skyrmion_vortex_radius = Label("Skyrmion/Vortex Radius (nm)")
        self.property_skyrmion_vortex_radius = FloatText(value=10, visible=False, disabled = True)
        self.label_domain_wall_width = Label("Wall width (nm)")
        self.property_domain_wall_width = FloatText(value=10, visible=False, disabled = True)

        self.box_skyrmion_vortex_config = Box([self.label_skyrmion_vortex_radius, self.property_skyrmion_vortex_radius], visible=False)
        self.box_domain_wall_config = Box([self.property_domain_wall_width], visible=False)
        self.property_initial_magnetisation.observe(on_change_magnetisation_type)
        self.page2 = Box([self.box_initial_magnetisation, self.box_domain_wall_config, self.box_skyrmion_vortex_config])


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
        self.property_rununtil = FloatText(value=10e-9, disabled=True)
        self.property_stopping_mxHxm = FloatText(value=0.01, disabled=False)
        self.get_code_button = Button(description="Get Code!")
        self.page3 = Box([HBox([self.label_dt, self.property_dt]),
                          self.property_saveevery, self.property_maxsteps,
                          self.label_simtype, self.property_simtype,
                          self.property_stopping_mxHxm,
                          self.property_rununtil])

        self.code_output = Textarea(value="")
        self.code_output.width = '600px'
        self.code_output.height = '400px'

        self.page4 = Box([self.get_code_button, self.code_output])

        self.get_code_button.on_click(get_code)

        # Header, assemble final layout

        self.maintitle = Label("OOMMFC - A Python GUI for setting up OOMMF Simulations")
        self.maintitle.layout.padding = '10px'
        self.tabs = Accordion([self.page0, self.page1, self.page2, self.page3, self.page4])
        self.tabs.set_title(0, 'Mesh')
        self.tabs.set_title(1, 'Interactions')
        self.tabs.set_title(2, 'Initial Magnetisation')
        self.tabs.set_title(3, 'Simulation Parameters')
        self.tabs.set_title(4, 'Generate Code')
        self.GUI = Box((self.maintitle, self.tabs))


    def print_dir(self):
        print(dir(self))
