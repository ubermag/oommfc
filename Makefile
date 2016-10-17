# convenience targets for developers
#
# test code is duplicated from .travis.yml
#

test: test-all #test-ipynb

# run all tests to get coverage info
test-all:
	py.test --cov=oommfc --cov-config .coveragerc

# run only tests that don't need oommf (fast)
test-not-oommf:
	py.test -v -m "not oommf"

test-oommf:
	py.test -v -m "oommf"

# we are currently not testing notebooks. Should we?
test-ipynb:
	py.test --nbval docs/ipynb/*.ipynb


# run TESTs in Docker container (TESTD). The commands below are copied
# from .travis.yml (excluding coverage) This is a
# convenience target to run the Travis tests (inside container)
# locally.
#
# Also modified to run the 'fast' non-oommf tests first,
# then the oommf tests.

testd:
	docker build -t dockertestimage .
	# run tests in docker, first non-oommf, then oommf
	docker run -e ci_env -ti dockertestimage /bin/bash -c "cd oommfc && python3 -m pytest -s -l -v -m 'not oommf'"
	docker run -e ci_env -ti dockertestimage /bin/bash -c "cd oommfc && python3 -m pytest -s -l -v -m 'oommf'"
