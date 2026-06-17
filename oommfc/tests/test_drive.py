import pytest
from micromagneticdata.testing.drive import *  # noqa: F403


@pytest.fixture
def calculator_script_content():
    return "MIF"


# Additional oommf specific tests


def test_ovf2vtk(self, tmp_path):
    self.data[0].ovf2vtk(dirname=tmp_path)

    def test_to_xarray(self):
        for drive in self.data:
            assert isinstance(drive.to_xarray(), xr.DataArray)
            assert all(
                item in drive.to_xarray().attrs.items() for item in drive.info.items()
            )
            if len(drive._step_files) != 1:
                assert len(drive.to_xarray()[drive.table.x]) == len(drive._step_files)
                assert np.allclose(
                    drive.to_xarray()[drive.table.x].values,
                    drive.table.data[drive.table.x].to_numpy(),
                )

            if drive.info["driver"] == "HysteresisDriver":
                assert all(
                    np.allclose(
                        drive.to_xarray()[f"B{i}_hysteresis"].values,
                        drive.table.data[f"B{i}_hysteresis"].to_numpy(),
                    )
                    for i in "xyz"
                )
