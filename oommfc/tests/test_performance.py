# import pytest

# @pytest.mark.xfail
def test_macrospin():
    """Test that runs an OOMMF simulation that basically doesn't do much:
    it computes the time development of a macrospin for a very short time.
    We can use this to test the overhead of starting up OOMMF."""
    import os
    import time
    import oommfc as oc
    import discretisedfield as df

    # define macro spin (i.e. one discretisation cell)
    p1 = (0, 0, 0)            # all lengths in metre
    p2 = (5e-9, 5e-9, 5e-9)
    cell = (5e-9, 5e-9, 5e-9)
    mesh = oc.Mesh(p1=p1, p2=p2, cell=cell)

    initial_m = (1, 0, 0)     # vector in x direction
    Ms = 8e6  # magnetisation saturation (A/m)
    m = df.Field(mesh, value=initial_m, norm=Ms)

    zeeman = oc.Zeeman(H=(0, 0, 5e6)) # external magnetic field (A/m)

    gamma = 2.211e5  # gyrotropic ration
    alpha = 0.05 # Gilbert damping

    runid = "tmp-macrospin-null-op"
    system = oc.System(name=runid)
    system.hamiltonian = zeeman
    system.m = m
    system.dynamics = oc.Precession(gamma) + oc.Damping(alpha)
    print("==========================================")
    print("Starting measurement through oommfc...")

    td = oc.TimeDriver()
    start = time.time()
    td.drive(system, t=0.001e-9, n=1)
    stop = time.time()
    duration = stop - start
    print("Duration of calling OOMMF through oommfc: {:.4}s".format(duration))


    print("==========================================")
    print("Starting measurement through oommfc...")


    # now do the same thing 'more directly':
    start = time.time()
    retvalue = os.system("cd tmp-macrospin-null-op && " +
                         "tclsh $OOMMFTCL boxsi +fg " +
                         "tmp-macrospin-null-op.mif -exitondone 1")
    stop = time.time()
    # did the exeuction complete correctly?
    assert retvalue == 0, "Something went wrong calling OOMMF directly."

    print("==========================================")
    duration2 = stop - start
    print("Duration of calling through os.system OOMMF: {:.4}s".format(duration2))
    # use the direct call as the base line (that's duration2)
    difference = duration - duration2
    reldiff = difference / duration2
    print("Difference between oommfc and os.system call is {:.4}s = {:.4}%".format(
        difference, reldiff * 100))

    # Calling OOMMF should not take 6 seconds. Let's say this should
    # be doable in 3, hopefully this also works on travis.
    assert duration2 <= 3.0, "{} should be < 3 seconds".format(duration2)

    # risky test: the folloming could fail if the run time is very short and
    # oommfc is hugely effective in starting OOMMF. THen we need to update this
    # next assert. It's meant to be a sanity check.
    assert reldiff > 0, "Direct call to OOMMF is slower - probably something went wrong?"

    # Here we could add a test criterion, that requires that
    # we only have a 50% overhead. This is maybe too forgiving - we should aim
    # to reduce this .
    assert reldiff < 0.5, "Actual absdiff={:.4}s, reldiff={:.4} > 0.5".format(difference, reldiff)


if __name__ == "__main__":
    test_macrospin()
