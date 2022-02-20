"""Tasks to release the package."""
import os
import shutil

import iniconfig
import pytest
import tomli
from invoke import Collection, task

PYTHON = 'python'
ns = Collection()


@task
def build_dists(c):
    """Build sdist and wheel."""
    if os.path.exists('dist'):
        shutil.rmtree('dist')
    c.run(f'{PYTHON} -m build')


@task(build_dists)
def upload(c):
    """Upload package to PyPI."""
    c.run('twine upload dist/*')


@task
def release(c):
    """Run the whole release process.

    Steps:
    - Pull all changes in ``master``.
    - Tag last commit using version information from setup.cfg/pyproject.toml.
    - Update the ``latest`` tag to point to the last commit.
    - Build package (``sdist`` and ``wheel``).
    - Upload package to PyPI.
    - Push new tags.
    """
    c.run('git checkout master')
    c.run('git pull')

    version = iniconfig.IniConfig('setup.cfg').get('metadata', 'version')
    # sanity checks while we have two places containing the version.
    with open('pyproject.toml', 'rb') as f:
        toml_version = tomli.load(f)['project']['version']
    assert toml_version == version, ('Different versions in pyproject.toml and'
                                     ' setup.cfg. Aborting.')

    c.run(f'git tag {version}')  # fails if the tag exists
    c.run('git tag -f latest')  # `latest` tag for binder

    build_dists(c)
    upload(c)

    c.run('git push -f --tags')
    c.run('git push')


ns.add_task(build_dists)
ns.add_task(upload)
ns.add_task(release)

test_collection = Collection('test')


@task
def unittest(c):
    """Run unittests."""
    import oommfc
    oommfc.test()


@task
def coverage(c):
    """Run unittests with coverage."""
    pytest.main(['-v', '--cov', 'oommfc', '--cov-report', 'xml'])


@task
def docs(c):
    """Run doctests."""
    pytest.main(['-v', '--doctest-modules', '--ignore',
                 'oommfc/tests', 'oommfc'])


@task
def ipynb(c):
    """Test notebooks."""
    pytest.main(['-v', '--nbval', '--sanitize-with', 'nbval.cfg',
                 'docs'])


@task
def pycodestyle(c):
    """Test pycodestyle.

    Will be replaces with flake8.
    """
    c.run(f'{PYTHON} -m pycodestyle --filename=*.py .')


@task(unittest, docs, ipynb, pycodestyle)
def all(unittest):
    """Run all tests."""


test_collection.add_task(unittest)
test_collection.add_task(docs)
test_collection.add_task(ipynb)
test_collection.add_task(pycodestyle)
test_collection.add_task(all)
ns.add_collection(test_collection)
