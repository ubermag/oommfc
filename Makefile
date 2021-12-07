PROJECT=oommfc
IPYNBPATH=docs/*.ipynb
PYTHON?=python

test-unittests:
	$(PYTHON) -c "import sys; import $(PROJECT); sys.exit($(PROJECT).test())"

test-coverage:
	$(PYTHON) -m pytest -v --cov=$(PROJECT) --cov-report=xml

test-docs:
	$(PYTHON) -m pytest -v --doctest-modules --ignore=$(PROJECT)/tests $(PROJECT)

test-ipynb:
	$(PYTHON) -m pytest -v --nbval --sanitize-with nbval.cfg $(IPYNBPATH)

test-pycodestyle:
	$(PYTHON) -m pycodestyle --filename=*.py .

test-all: test-unittests test-docs test-ipynb test-pycodestyle

build-dists:
	rm -rf dist/
	$(PYTHON) setup.py sdist bdist_wheel

release: build-dists
	twine upload dist/*
