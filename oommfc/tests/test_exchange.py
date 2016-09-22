from micromagneticmodel.tests.test_exchange import TestExchange
from oommfc.hamiltonian import Exchange


class TestExchange(TestExchange):
    def test_script(self):
        for A in self.valid_args:
            exchange = Exchange(A)

            script = exchange.script()
            assert script.count("\n") == 5
            assert script[0] == "#"
            assert script[-1] == "\n"
            
            lines = script.split("\n")
            assert len(lines) == 6
            assert lines[0] == "# UniformExchange"
            assert lines[1] == "Specify Oxs_UniformExchange {"
            assert lines[2] == "  A {}".format(A)
            assert lines[3] == "}"
