import oommfc as oc


class TestHamiltonian:
    def setup(self):
        A = 1e-12
        self.exchange = oc.Exchange(A)
        H = (0, 0, 1.2e6)
        self.zeeman = oc.Zeeman(H)
        K = 1e4
        u = (0, 1, 0)
        self.uniaxialanisotropy = oc.UniaxialAnisotropy(K, u)
        self.demag = oc.Demag()

        self.terms = [self.exchange,
                      self.zeeman,
                      self.uniaxialanisotropy,
                      self.demag]

    def test_script(self):
        hamiltonian = oc.Hamiltonian()
        for term in self.terms:
            hamiltonian.add(term)

        script = hamiltonian.script()

        assert script.count("#") == 4
        assert script.count("Specify") == 4
        assert script[0] == "#"
        assert script[-1] == "\n"

        assert "UniformExchange" in script
        assert "FixedZeeman" in script
        assert "UniaxialAnisotropy" in script
        assert "Demag" in script

        assert "A" in script
        assert "K1" in script
        assert "axis" in script
        assert "multiplier" in script
        assert "vector" in script
        assert "field" in script
