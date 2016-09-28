import oommfc as oc
import micromagneticmodel.tests as mmt


class TestExchange(mmt.TestExchange):
    def test_script(self):
        for A in self.valid_args:
            exchange = oc.Exchange(A)

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
