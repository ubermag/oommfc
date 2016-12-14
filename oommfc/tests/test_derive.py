import os
import shutil
import oommfc as oc
import discretisedfield as df


class TestDerive:
    def setup(self):
        self.name = "derive_tests"
        if os.path.exists(self.name):
            shutil.rmtree(self.name)

        self.system = oc.System(name=self.name)
        self.system.hamiltonian += oc.Exchange(A=1e-12)
        self.system.hamiltonian += oc.Demag()
        self.system.hamiltonian += oc.Zeeman(H=(8e6, 0, 0))
        self.system.hamiltonian += oc.UniaxialAnisotropy(K=1e4, u=(0, 0, 1))
        mesh = oc.Mesh(p1=(0, 0, 0), p2=(10e-9, 10e-9, 2e-9),
                       cell=(1e-9, 1e-9, 1e-9))
        self.system.m = df.Field(mesh, value=(0, 0, 1), norm=8e6)

    def test_energy(self):
        hamiltonian = self.system.hamiltonian
        assert isinstance(hamiltonian.exchange.energy, float)
        assert isinstance(hamiltonian.exchange.energy, float)
        assert isinstance(hamiltonian.exchange.energy, float)
        assert isinstance(hamiltonian.exchange.energy, float)
        assert isinstance(hamiltonian.energy, float)
        if os.path.exists(self.name):
            shutil.rmtree(self.name)

    def test_energy_density(self):
        hamiltonian = self.system.hamiltonian
        assert isinstance(hamiltonian.exchange.energy_density, df.Field)
        assert isinstance(hamiltonian.exchange.energy_density, df.Field)
        assert isinstance(hamiltonian.exchange.energy_density, df.Field)
        assert isinstance(hamiltonian.exchange.energy_density, df.Field)
        assert isinstance(hamiltonian.energy_density, df.Field)
        assert hamiltonian.energy_density.dim == 1
        if os.path.exists(self.name):
            shutil.rmtree(self.name)

    def test_effective_field(self):
        hamiltonian = self.system.hamiltonian
        assert isinstance(hamiltonian.exchange.effective_field, df.Field)
        assert isinstance(hamiltonian.exchange.effective_field, df.Field)
        assert isinstance(hamiltonian.exchange.effective_field, df.Field)
        assert isinstance(hamiltonian.exchange.effective_field, df.Field)
        assert isinstance(hamiltonian.effective_field, df.Field)
        assert hamiltonian.effective_field.dim == 3
        if os.path.exists(self.name):
            shutil.rmtree(self.name)

    
