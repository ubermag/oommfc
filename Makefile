PROJECT=oommfc
IPYNBPATH=docs/ipynb/*.ipynb
CODECOVTOKEN=a253c171-1619-4812-944c-89918bf5c98d
PYTHON?=python3

test:
	$(PYTHON) -m pytest

# run tests as the users would (via test())
test-test:
	$(PYTHON) -c "import oommfc as c; import sys; sys.exit(c.test())"

test-coverage:
	$(PYTHON) -m pytest --cov=$(PROJECT) --cov-config .coveragerc oommfc/tests/*test*
	@# Touch used to avoid failure of the cat command if file is not created.
	@touch travis_test_performance_summary.txt
	cat travis_test_performance_summary.txt

test-ipynb:
	$(PYTHON) -m pytest --nbval-lax $(IPYNBPATH)

test-docs:
	$(PYTHON) -m pytest --doctest-modules --ignore=$(PROJECT)/tests $(PROJECT)

test-all: test-test test-coverage test-ipynb test-docs

test-oommf:
	$(PYTHON) -m pytest -m "oommf"

test-not-oommf:
	$(PYTHON) -m pytest -m "not oommf"

upload-coverage: SHELL:=/bin/bash
upload-coverage:
	bash <(curl -s https://codecov.io/bash) -t $(CODECOVTOKEN)

travis-build: SHELL:=/bin/bash
travis-build:
	ci_env=`bash <(curl -s https://codecov.io/env)`
	docker build -t dockertestimage .
	docker run --privileged -e ci_env -ti -d --name testcontainer dockertestimage
	docker exec testcontainer make test-all
	docker exec testcontainer make upload-coverage
	docker stop testcontainer
	docker rm testcontainer

test-docker:
	docker build -t dockertestimage .
	docker run --privileged -ti -d --name testcontainer dockertestimage
	docker exec testcontainer make test-all
	docker stop testcontainer
	docker rm testcontainer

build-dists:
	rm -rf dist/
	$(PYTHON) setup.py sdist
	$(PYTHON) setup.py bdist_wheel

release: build-dists
	twine upload dist/*

