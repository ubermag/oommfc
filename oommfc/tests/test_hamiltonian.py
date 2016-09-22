import oommfc.hamiltonian as oh


class TestHamiltonian:
    def setup(self):
        A = 1e-12
        self.exchange = oh.Exchange(A)
        H = (0, 0, 1.2e6)
        self.zeeman = oh.Zeeman(H)
        K = 1e4
        u = (0, 1, 0)
        self.uniaxialanisotropy = oh.UniaxialAnisotropy(K, u)
        self.demag = oh.Demag()

        self.terms = [self.exchange,
                      self.zeeman,
                      self.uniaxialanisotropy,
                      self.demag]

    def test_script(self):
        hamiltonian = oh.Hamiltonian()
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
