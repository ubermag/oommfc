import pytest
import oommfc as oc
import discretisedfield as df
import micromagneticmodel as mm


class TestMagnetoElastic:
    def setup(self):
        p1 = (-7e-9, -5e-9, -4e-9)
        p2 = (7e-9, 5e-9, 4e-9)
        self.region = df.Region(p1=p1, p2=p2)
        self.cell = (1e-9, 1e-9, 1e-9)
        self.subregions = {'r1': df.Region(p1=(-7e-9, -5e-9, -4e-9),
                                           p2=(0, 5e-9, 4e-9)),
                           'r2': df.Region(p1=(0, -5e-9, -4e-9),
                                           p2=(7e-9, 5e-9, 4e-9))}

    @pytest.mark.travis
    def test_scalar_scalar_vector_vector(self):
        name = 'magnetoelastic_scalar_scalar_vector_vector'

        B1 = 1e5
        B2 = 1e6
        e_diag = (1, 1, 1)
        e_offdiag = (0, 0, 0)
        Ms = 1e6

        system = mm.System(name=name)
        system.energy = mm.MagnetoElastic(B1=B1, B2=B2, e_diag=e_diag,
                                          e_offdiag=e_offdiag)

        mesh = df.Mesh(region=self.region, cell=self.cell)
        system.m = df.Field(mesh, dim=3, value=(0, 0.3, 1), norm=Ms)

        md = oc.MinDriver()
        md.drive(system)

        # Assertions have to be invented. Checks only if it runs.
