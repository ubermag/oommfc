import os
import pytest
import oommfc as oc
import micromagneticmodel as mm


def test_save_delete():
    system = mm.examples.macrospin()

    td = oc.TimeDriver()
    td.drive(system, t=1e-12, n=5, save=True, overwrite=True)

    assert os.path.exists(os.path.join(system.name, 'drive-0'))

    with pytest.raises(FileExistsError):
        system.drive_number = 0
        td.drive(system, t=1e-12, n=5, save=True)

    assert os.path.exists(os.path.join(system.name, 'drive-0'))
    assert not os.path.exists(os.path.join(system.name, 'drive-1'))

    system.drive_number = 0
    td.drive(system, t=1e-12, n=5, save=False)

    assert os.path.exists(os.path.join(system.name, 'drive-0'))
    assert not os.path.exists(os.path.join(system.name, 'drive-1'))

    td.drive(system, t=1e-12, n=5, save=True, overwrite=True)

    assert os.path.exists(os.path.join(system.name, 'drive-0'))
    assert os.path.exists(os.path.join(system.name, 'drive-1'))

    oc.delete(system)

    assert not os.path.exists(system.name)

    with pytest.raises(FileNotFoundError):
        oc.delete(system)
