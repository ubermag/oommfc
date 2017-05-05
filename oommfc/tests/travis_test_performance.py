import os
import time
import pytest
import shutil
import oommfc as oc

@pytest.mark.oommf
@pytest.mark.travis
def test_performance():
    """Test that runs an OOMMF simulation that basically doesn't do much:
    it computes the time development of a macrospin for a very short time.
    We can use this to test the overhead of starting up OOMMF.

    Running the test on 20 March 2017 on Travis (see https://travis-ci.org/joommf/oommfc/builds/212906740)
    gave this performance:

    	2017/3/20 8:49: Calling OOMMF (example-macrospin/example-macrospin.mif) ... [0.4s]
    	<1> mmarchive killed
    	<2> mmarchive killed
    	<3> mmarchive killed
    	Duration of calling OOMMF through oommfc: 1.067s
    	oommfc.oommf.status(): {'docker': True, 'host': True}
    	Start: "/usr/local/oommfc/example-macrospin/example-macrospin.mif"
    	Options: -exitondone 1 -threads 2
    	Boxsi version 1.2.1.0
    	Running on: 9bedd4e404e5
    	OS/machine: Linux/x86_64
    	User: root	PID: 13914
    	Number of threads: 2
    	Mesh geometry: 1 x 1 x 1 = 1 cells
    	Checkpoint file: /usr/local/oommfc/example-macrospin/example-macrospin.restart
    	Boxsi run end.
    	==========================================
    	Duration of calling through os.system OOMMF: 1.32s
    	Difference between oommfc and os.system call is -0.2536s = -19.21%
    	==================== 2 failed, 128 passed in 267.38 seconds ====================

    This means: the actual call of OOMMF took 0.4s (reported by our
    code), the overhead of doing this through OOMMFC meant that this
    acumulated to 1.067s. It is not clear where this overhead comes
    from and why it should be that much.

    Calling OOMMF directly through os.system took 1.32s. One would
    expect that this is a similar number to the 0.4s, so again some
    questions. Of course the above is only one data point, and could
    depend on load fluctuations on the Travis CI infrastructure.

    In any case, this shows that overheads of the order of 1 second
    are reasonable, and shouldn't be exceeded.

    Hans, Dresden, 20 March 2017

    """
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

    # Also write output to file (might be useful to get the data if the test passes)
    with open('travis_test_performance_summary.txt', 'tw') as f:
        f.write("=================================================================\n")
        f.write("Performance test oommfc/tests/travis_test_performance.py results:\n")
        f.write("\n")
        f.write("Call through oommfc:    {:.4}s\n".format(duration))
        f.write("Call through os.system: {:.4}s\n".format(duration2))
        f.write("Difference:             {:.4}s\n".format(difference))
        f.write("Relative difference:    {:.4}%\n".format(reldiff*100))
        f.write("-----------------------------------------------------------------\n")
        f.write("This data is from {}.\n".format(time.asctime()))
        f.write("-----------------------------------------------------------------\n")

    # Now onto the testing. These may have to be fine tuned, depending
    # on how reproducible the hardware load on the Travis system is.

    # Calling OOMMF should not take 6 seconds (as we have seen on some
    # tests this week). Let's say this should be doable in 2,
    # hopefully this also works on travis.
    assert duration2 <= 2.0, "{} should be < 2 seconds".format(duration2)

    # Here we could add a test criterion, that requires that
    # we only have a 100% overhead. This is maybe too forgiving - we should aim
    # to reduce this .
    assert abs(reldiff) < 1.0, \
        "Actual absdiff={:.4}s, reldiff={:.4} > 0.5".format(difference, reldiff)

    # The overhead should be under one second. Again, we shoud aim
    # towards a harsher criterion in due course.
    assert difference < 1.0, \
        "overhead from OOMMFC is {:.4}s and exceeding 1second".format(difference)

    shutil.rmtree("example-macrospin")

if __name__ == "__main__":
    test_performance()
