PROJECT=oommfc
IPYNBPATH=docs/ipynb/*.ipynb
CODECOVTOKEN=a253c171-1619-4812-944c-89918bf5c98d
PYTHON?=python3

test: test-coverage test-ipynb

test-all:
	$(PYTHON) -m pytest

test-ipynb:
	$(PYTHON) -m pytest --nbval-lax $(IPYNBPATH)

test-coverage:
	$(PYTHON) -m pytest --cov=$(PROJECT) --cov-config .coveragerc . oommfc/tests/travis_*

	@# if performance file has been created, display the results
	@# (touch is only used to guarantee the file exists, and avoid failure of the cat command)
	@touch travis_test_performance_summary.txt
	cat travis_test_performance_summary.txt


# this target should be run in an environment where docker is installed
# but the deamon not running. See https://github.com/joommf/oommfc/issues/13
test-no-docker-running-raises-error:
	$(PYTHON) -m pytest oommfc/tests/no_docker_running_raises_error.py

upload-coverage: SHELL:=/bin/bash
upload-coverage:
	bash <(curl -s https://codecov.io/bash) -t $(CODECOVTOKEN)

travis-build: test-coverage upload-coverage test-ipynb

test-docker:
	docker build -t dockertestimage .
	docker run --privileged -ti -d --name testcontainer dockertestimage
	docker exec testcontainer $(PYTHON) -m pytest
	docker exec testcontainer $(PYTHON) -m pytest --nbval-lax $(IPYNBPATH)
	docker stop testcontainer
	docker rm testcontainer

test-oommf:
	$(PYTHON) -m pytest -m "oommf"

test-not-oommf:
	$(PYTHON) -m pytest -m "not oommf"

build-dists:
	rm -rf dist/
	$(PYTHON) setup.py sdist
	$(PYTHON) setup.py bdist_wheel

release: build-dists
	twine upload dist/*
