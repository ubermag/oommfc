from oommfc import BoxAtlas, RectangularMesh, Sim
from oommfc.energies import UniformExchange, FixedZeeman, Demag
from oommffield import Field


class TestSim(object):
    def setup(self):
        cmin = (0, 0, 0)
        cmax = (5, 5, 5)
        atlas = BoxAtlas(cmin, cmax)
        mesh = RectangularMesh(atlas, (1, 1, 1))
        self.sim = Sim(mesh, 1e6, 'test_sim')

    def test_sim_init(self):
        assert self.sim.alpha == 1
        assert isinstance(self.sim.m, Field)
        assert isinstance(self.sim.energies, list)
        assert len(self.sim.energies) == 0
        assert self.sim.dirname == 'test_sim/'
        assert self.sim.mif_filename == 'test_sim/test_sim.mif'

    def test_add(self):
        exchange = UniformExchange(1e-12)

        assert len(self.sim.energies) == 0
        self.sim.add(exchange)
        assert len(self.sim.energies) == 1

    def test_set_H(self):
        zeeman = FixedZeeman((0, 0, 0))

        assert len(self.sim.energies) == 0
        self.sim.add(zeeman)
        assert len(self.sim.energies) == 1
        assert self.sim.energies[0].H == (0, 0, 0)
        self.sim.set_H((1, 3, 2e-3))
        assert len(self.sim.energies) == 1
        assert self.sim.energies[0].H == (1, 3, 2e-3)

    def test_set_m(self):
        self.sim.set_m((1, 2, -1))
        assert self.sim.m.f[0, 0, 0, 0] == 1
        assert self.sim.m.f[0, 0, 0, 1] == 2
        assert self.sim.m.f[0, 0, 0, 2] == -1

        m_average = self.sim.m_average()
        assert m_average[0] == 1
        assert m_average[1] == 2
        assert m_average[2] == -1

        def m_init(pos):
            return (1, 0, -5)
        self.sim.set_m(m_init)
        assert self.sim.m.f[0, 0, 0, 0] == 1
        assert self.sim.m.f[0, 0, 0, 1] == 0
        assert self.sim.m.f[0, 0, 0, 2] == -5

        m_average = self.sim.m_average()
        assert m_average[0] == 1
        assert m_average[1] == 0
        assert m_average[2] == -5
