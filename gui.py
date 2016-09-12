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
        # Todo: Dictionary as data model?

        self.dict = {}

        def on_dimension_change(b):
            if self.property_dim.value == 1:
                self.property_Ly.disabled = True
                self.property_Lz.disabled = True
                self.property_dy.disabled = True
                self.property_dz.disabled = True
            elif self.property_dim.value == 2:
                self.property_Ly.disabled = False
                self.property_Lz.disabled = True
                self.property_dy.disabled = False
                self.property_dz.disabled = True
            elif self.property_dim.value == 3:
                self.property_Ly.disabled = False
                self.property_Lz.disabled = False
                self.property_dy.disabled = False
                self.property_dz.disabled = False

        def on_change_anis(c):
            if not self.property_anis_enabled.value:
                self.property_K.disabled = True
                self.property_anis_axis.disabled = True
            else:
                self.property_K.disabled = False
                self.property_anis_axis.disabled = False

        def on_change_exch(c):
            if not self.property_faexch_enabled.value:
                self.property_exchconst.disabled = True
            else:
                self.property_exchconst.disabled = False

        def on_select_init_mag(c):
            # Not implementing yet but left here so don't have to rewrite
            if dim.value == 1:
                dim.options = ['Constant', 'Domain Wall']
            if dim.value == 2 or dim.value == 3:
                dim.options = ['Constant', 'Domain Wall', 'Vortex', 'Skyrmion']

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
            code = 'import oommfc'
            code += assemble_mesh_code()
            code += assemble_interactions_code()
            code += assemble_properties_code()
            self.code_output.value = code

        def assemble_mesh_code():
            update_dictionary()
            code = ""
            dim = self.dict['dim']

            if dim == 1:
                Lx = self.dict['Lx']
                Ly = 1
                Lz = 1
                dx = self.dict['dx']
                dy = 1
                dz = 1
            elif dim == 2:
                Lx = self.dict['Lx']
                Ly = self.dict['Ly']
                Lz = 1
                dx = self.dict['dx']
                dy = self.dict['dy']
                dz = 1
            elif dim == 3:
                Lx = self.dict['Lx']
                Ly = self.dict['Ly']
                Lz = self.dict['Lz']
                dx = self.dict['dx']
                dy = self.dict['dy']
                dz = self.dict['dz']
            Ms = self.dict['Ms']
            code = textwrap.dedent("""\

                   atlas = oommfc.BoxAtlas((0, 0, 0), ({}, {}, {}))
                   mesh = oommfc.RectangularMesh(atlas, ({}, {}, {}))
                   sim = oommfc.Sim(mesh, {})
                   """)

            return code.format(Lx, Ly, Lz, dx, dy, dz, Ms)

        def assemble_interactions_code():
            code = ""
            axis = self.dict['anis_axis']
            ax_x, ax_y, ax_z = 0, 0, 0
            if 1 in axis or axis == 1:
                ax_x = 1
            if 2 in axis or axis == 2:
                ax_y = 1
            if 3 in axis or axis == 3:
                ax_z = 1
            if self.dict['exch_enabled']:
                code += textwrap.dedent("""\
                    exchange = oommfc.energies.UniformExchange({})
                    sim.add(exchange)
                    """).format(self.dict['exchconst'])

            if self.dict['demag_enabled']:
                code += textwrap.dedent("""\

                    demag = oommfc.energies.Demag()
                    sim.add(demag)

                    """)
            if self.dict['anis_enabled']:
                code += textwrap.dedent("""\

                    anis = oommfc.energies.UniaxialAnisotropy(Ku={},
                                                            axis=({},{},{}))
                    sim.add(anis)

                    """).format(self.dict['K'],
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

        # Page 1 : Mesh Shape

        self.label_dim = Label("Dimensions")
        self.property_dim = IntSlider(value=1, min=1, max=3, step=1)
        self.label_lengths = Label("Mesh Lengths")
        self.property_Lx = IntText("1", description="Lx")
        self.property_Ly = IntText("1", description="Ly", disabled=True)
        self.property_Lz = IntText("1", description="Lz", disabled=True)
        self.property_scale = FloatText(description="scale (m)", value=1e-9)
        self.label_discretisation = Label("Discretisation")
        self.property_dx = FloatText("1", description="dx")
        self.property_dy = FloatText("1", description="dy", disabled=True)
        self.property_dz = FloatText("1", description="dz", disabled=True)

        self.property_dim.observe(on_dimension_change)
        self.page1 = widgets.Box((self.label_dim, self.property_dim,
                                  self.label_lengths, self.property_Lx,
                                  self.property_Ly, self.property_Lz,
                                  self.label_discretisation, self.property_dx,
                                  self.property_dy, self.property_dz,
                                  ))

        # Page 2 : Interactions

        self.Mslab = Label("Saturation Magnetization (A/m)")
        self.property_Ms = FloatText(value=8e5, readout_format='.5e')
        self.Msbox = Box([self.Mslab, self.property_Ms])
        self.exchlab = Label("Exchange (J/m)")
        self.property_exch_enabled = Checkbox(
            value=True, description="Enabled")
        self.property_exchconst = FloatText(value=13e-12, readout_format='.5e')
        self.property_exch_enabled.observe(on_change_exch)
        self.exchbox = Box(
            [HBox([self.exchlab, self.property_exch_enabled]),
             self.property_exchconst])
        self.demaglab = Label("Demagnetisation")
        self.property_demag_enabled = Checkbox(
            value=False, description="Enabled")
        self.demagbox = HBox([self.demaglab, self.property_demag_enabled])
        self.anislab = Label("Uniaxial Anisotropy")
        self.property_anis_enabled = Checkbox(
            value=False, description="Enabled")
        self.property_K = FloatText(value=1.3e-11, disabled=True)
        self.property_anis_axis = SelectMultiple(description="Axis",
                                                 options={
                                                     'x': 1, 'y': 2, 'z': 3},
                                                 disabled=True)
        self.property_anis_enabled.observe(on_change_anis)
        self.anisbox = Box([HBox([self.anislab, self.property_anis_enabled]),
                            self.property_K, self.property_anis_axis])

        self.page2 = Box([self.Msbox, self.exchbox, self.demagbox,
                          self.anisbox])

        # Page 3 - Initial Magnetisation
        # Put this in later after  are working
        # self.init_mag = Select(options=['Constant', 'Domain Wall']) #
        # 'Vortex', 'Skyrmion', for 2D and 3D.

        # Page 3 : Simulation Parameters

        self.label_dt = Label("dt (s)")
        self.property_dt = FloatText(value=1e-9)

        # self.init_mag.observe
        self.m0 = Box([FloatText(description="m0_x", min=-1, max=1, value=1),
                       FloatText(description="m0_y", min=-1, max=1, value=0),
                       FloatText(description="m0_z", min=-1, max=1, value=0)])

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

        self.maintitle = Label("oommfc")
        self.maintitle.layout.padding = '10px'
        self.tabs = Accordion([self.page1, self.page2, self.page3, self.page4])
        self.tabs.set_title(0, 'Mesh')
        self.tabs.set_title(1, 'Interactions')
        self.tabs.set_title(2, 'Simulation Parameters')
        self.tabs.set_title(3, 'Generate Code')
        self.GUI = Box((self.maintitle, self.tabs))

    def get_mesh_code(self):
        pass

    def print_dir(self):
        print(dir(self))
