import discretisedfield as df
import micromagneticmodel as mm
import numpy as np
import pytest

import oommfc as oc


@pytest.fixture
def mesh():
    return df.Mesh(p1=(0, 0, 0), p2=(20e-9, 20e-9, 5e-9), cell=(5e-9, 5e-9, 5e-9))


def test_setup_scalar_parameter_positive_field(mesh, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    field = df.Field(mesh, nvdim=1, value=lambda p: 1e5 + p[0] * 1e12)
    mif, name = oc.scripts.setup_scalar_parameter(field, "K")
    assert name == "K_norm"
    assert "offset" not in mif  # unchanged output for non-negative fields
    written = df.Field.from_file("K.ovf")
    assert np.allclose(written.array[..., 0], field.array[..., 0])


def test_setup_scalar_parameter_negative_field(mesh, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    field = df.Field(mesh, nvdim=1, value=lambda p: -1e5 + p[0] * 1e12)
    mif, name = oc.scripts.setup_scalar_parameter(field, "K")
    offset = float(field.array.min())
    assert f"offset {offset}" in mif
    written = df.Field.from_file("K.ovf")
    assert np.all(written.array[..., 0] >= 0)
    # norm + offset (what Oxs_VecMagScalarField computes) gives back the input
    norm = np.linalg.norm(written.array, axis=-1)
    assert np.allclose(norm + offset, field.array[..., 0])


def test_negative_anisotropy_field(mesh, tmp_path, monkeypatch):
    """K < 0 given as a Field must behave like the same K given as a number."""
    monkeypatch.chdir(tmp_path)

    def relaxed_m(K):
        system = mm.System(name="negative_k")
        system.energy = mm.Exchange(A=1e-11) + mm.UniaxialAnisotropy(K=K, u=(0, 0, 1))
        system.m = df.Field(mesh, nvdim=3, value=(0.3, 0, 1), norm=8e5)
        oc.MinDriver().drive(system, verbose=0)
        return np.array(system.m.mean()) / 8e5

    m_number = relaxed_m(-1e5)
    m_field = relaxed_m(df.Field(mesh, nvdim=1, value=-1e5))
    assert abs(m_number[2]) < 1e-3  # easy plane: m lies in-plane
    assert np.allclose(m_field, m_number, atol=1e-3)
