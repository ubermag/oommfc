import os
import re
import glob
import json
import shutil
import oommfc as oc
import discretisedfield as df
import micromagneticmodel as mm


def test_info_file():
    name = 'info_file'

    L = 30e-9   # (m)
    cell = (10e-9, 15e-9, 5e-9)  # (m)
    A = 1.3e-11  # (J/m)
    Ms = 8e5  # (A/m)
    H = (1e6, 0.0, 2e5)  # (A/m)
    gamma0 = 2.211e5  # (m/As)
    alpha = 0.02

    region = df.Region(p1=(0, 0, 0), p2=(L, L, L))
    mesh = df.Mesh(region=region, cell=cell)
    system = mm.System(name=name)
    system.energy = mm.Exchange(A=A) + mm.Zeeman(H=H)
    system.dynamics = mm.Precession(gamma0=gamma0) + mm.Damping(alpha=alpha)
    system.m = df.Field(mesh, dim=3, value=(0.0, 0.25, 0.1), norm=Ms)

    # First (0) drive
    td = oc.TimeDriver()
    td.drive(system, t=25e-12, n=10, save=True, overwrite=True)

    dirname = os.path.join(name, 'drive-0')
    infofile = os.path.join(dirname, 'info.json')
    assert os.path.exists(dirname)
    assert os.path.isfile(infofile)

    with open(infofile) as f:
        info = json.loads(f.read())
    assert 'drive_number' in info.keys()
    assert 'date' in info.keys()
    assert 'time' in info.keys()
    assert 'driver' in info.keys()
    assert 'args' in info.keys()

    assert info['drive_number'] == 0
    assert re.findall(r'\d{4}-\d{2}-\d{2}', info['date']) is not []
    assert re.findall(r'\d{2}:\d{2}-\d{2}', info['time']) is not []
    assert info['driver'] == 'TimeDriver'
    assert isinstance(info['args'], dict)
    assert info['args']['t'] == 25e-12
    assert info['args']['n'] == 10

    # Second (1) drive
    md = oc.MinDriver()
    md.drive(system, save=True)

    dirname = os.path.join(name, 'drive-1')
    infofile = os.path.join(dirname, 'info.json')
    assert os.path.exists(dirname)
    assert os.path.isfile(infofile)

    with open(infofile) as f:
        info = json.loads(f.read())
    assert 'drive_number' in info.keys()
    assert 'date' in info.keys()
    assert 'time' in info.keys()
    assert 'driver' in info.keys()
    assert 'args' in info.keys()

    assert info['drive_number'] == 1
    assert re.findall(r'\d{4}-\d{2}-\d{2}', info['date']) is not []
    assert re.findall(r'\d{2}:\d{2}-\d{2}', info['time']) is not []
    assert info['driver'] == 'MinDriver'
    assert isinstance(info['args'], dict)
    assert info['args'] == {}

    oc.delete(system)
