PROJECT=oommfc
IPYNBPATH=docs/ipynb/*.ipynb
CODECOVTOKEN=a253c171-1619-4812-944c-89918bf5c98d

#test: test-coverage #test-ipynb

test-all:
	python3 -m pytest

test-ipynb:
	python3 -m pytest --nbval $(IPYNBPATH)

test-coverage:
	python3 -m pytest --cov=$(PROJECT) --cov-config .coveragerc

upload-coverage: SHELL:=/bin/bash
upload-coverage:
	bash <(curl -s https://codecov.io/bash) -t $(CODECOVTOKEN)

travis-build: test-coverage upload-coverage

test-docker:
	docker build -t dockertestimage .
	docker run --privileged -ti -d --name testcontainer dockertestimage
	docker exec testcontainer python3 -m pytest
	docker exec testcontainer python3 -m pytest --nbval-lax $(IPYNBPATH)
	docker stop testcontainer
	docker rm testcontainer

test-oommf:
	python3 -m pytest -m "oommf"

test-not-oommf:
	python3 -m pytest -m "not oommf"

pypitest-upload:
	python3 setup.py register -r pypitest
	python3 setup.py sdist upload -r pypitest

pypi-upload: pypitest-upload
	python3 setup.py sdist upload -r pypi
