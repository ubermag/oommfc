import oommfc as oc


def system_script(system):
    mif = oc.script.mesh_script(system.m.mesh)
    mif += oc.script.energy_script(system.energy)

    return mif
