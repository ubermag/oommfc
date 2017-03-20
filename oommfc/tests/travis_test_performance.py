import pytest

# Attempt to find out performance on travis

@pytest.mark.oommf
def test_macrospin():

    """Test that runs an OOMMF simulation that basically doesn't do much:
    it computes the time development of a macrospin for a very short time.
    We can use this to test the overhead of starting up OOMMF."""
    import os
    import time
    import oommfc as oc
    duration, mifpath = oc.test_oommf_overhead()

    # now do the same thing 'more directly':
    start = time.time()
    retvalue = os.system("tclsh $OOMMFTCL boxsi +fg " +
                         "{} -exitondone 1".format(mifpath))
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

    # risky test: the following could fail if the run time is very short and
    # oommfc is hugely effective in starting OOMMF. THen we need to update this
    # next assert. It's meant to be a sanity check.
    assert reldiff > 0, "Direct call to OOMMF is slower - probably something went wrong?"

    # Here we could add a test criterion, that requires that
    # we only have a 100% overhead. This is maybe too forgiving - we should aim
    # to reduce this .
    assert reldiff < 1.0, "Actual absdiff={:.4}s, reldiff={:.4} > 0.5".format(difference, reldiff)

    # The overhead should be under one second. Again, we shoud aim towards a harsher
    # criterion in due course.
    assert difference < 1.0, "overhead from OOMMFC is {:.4}s and exceeding 1second".\
        format(difference)

    # if all of the above pass, we like to see the printed output, so
    # put in a fail on purpose here
    assert False

if __name__ == "__main__":
    test_macrospin()
