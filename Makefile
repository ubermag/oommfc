PROJECT=oommfc
IPYNBPATH=docs/ipynb/*.ipynb
CODECOVTOKEN=8ac500f6-4ed4-4b0e-86a6-a8ed4184d788
PYTHON?=python3

test:
	$(PYTHON) -m pytest

test-test:
	$(PYTHON) -c "import sys; import $(PROJECT); sys.exit($(PROJECT).test())"

test-travis:
	$(PYTHON) -m pytest -m "travis"

test-coverage:
	$(PYTHON) -m pytest -m "not docker" --cov=$(PROJECT) --cov-config .coveragerc

test-docs:
	$(PYTHON) -m pytest --doctest-modules --ignore=$(PROJECT)/tests $(PROJECT)

test-ipynb:
	$(PYTHON) -m pytest --nbval-lax $(IPYNBPATH)

test-all: test-test test-coverage test-docs test-ipynb

test-all-travis: test-test test-travis test-coverage test-docs test-ipynb

upload-coverage: SHELL:=/bin/bash
upload-coverage:
	bash <(curl -s https://codecov.io/bash) -t $(CODECOVTOKEN)

travis-build: SHELL:=/bin/bash
travis-build:
	ci_env=`bash <(curl -s https://codecov.io/env)`
	docker build -f docker/Dockerfile -t dockertestimage .
	docker run -e ci_env -ti -d --name testcontainer dockertestimage
	docker exec testcontainer make test-all-travis
	docker exec testcontainer make upload-coverage
	docker stop testcontainer
	docker rm testcontainer

test-docker:
	docker build -f docker/Dockerfile -t dockertestimage .
	docker run -ti -d --name testcontainer dockertestimage
	docker exec testcontainer make test-all-travis
	docker stop testcontainer
	docker rm testcontainer

build-dists:
	rm -rf dist/
	$(PYTHON) setup.py sdist bdist_wheel

release: build-dists
	twine upload dist/*
