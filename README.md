# oommfc
Marijan Beg<sup>1,2</sup>, Ryan A. Pepper<sup>2</sup>, Thomas Kluyver<sup>1</sup>, and Hans Fangohr<sup>1,2</sup>

<sup>1</sup> *European XFEL GmbH, Holzkoppel 4, 22869 Schenefeld, Germany*  
<sup>2</sup> *Faculty of Engineering and the Environment, University of Southampton, Southampton SO17 1BJ, United Kingdom*  

| Description | Badge |
| --- | --- |
| Latest release | [![PyPI version](https://badge.fury.io/py/oommfc.svg)](https://badge.fury.io/py/oommfc) |
|                | [![Anaconda-Server Badge](https://anaconda.org/conda-forge/oommfc/badges/version.svg)](https://anaconda.org/conda-forge/oommfc) |
| Build | [![Build Status](https://travis-ci.org/joommf/oommfc.svg?branch=master)](https://travis-ci.org/joommf/oommfc) |
|       | [![Build status](https://ci.appveyor.com/api/projects/status/a1cp833x8trei0d8?svg=true)](https://ci.appveyor.com/project/marijanbeg/oommfc) |
| Coverage | [![codecov](https://codecov.io/gh/joommf/oommfc/branch/master/graph/badge.svg)](https://codecov.io/gh/joommf/oommfc) |
| Documentation | [![Documentation Status](https://readthedocs.org/projects/oommfc/badge/?version=latest)](http://oommfc.readthedocs.io/en/latest/?badge=latest) |
| Binder | [![Binder](https://mybinder.org/badge.svg)](https://mybinder.org/v2/gh/joommf/oommfc/master?filepath=index.ipynb) |
| Dependecies | [![Requirements Status](https://requires.io/github/joommf/oommfc/requirements.svg?branch=master)](https://requires.io/github/joommf/oommfc/requirements/?branch=master) |
| License | [![License](https://img.shields.io/badge/License-BSD%203--Clause-blue.svg)](https://opensource.org/licenses/BSD-3-Clause) |

## About

`oommfc` is a Python package that provides:

- An interface to the Object Oriented MicroMagnetic Framework [OOMMF](https://math.nist.gov/oommf/)

- Integration of OOMMF simulations into the [Jupyter](http://jupyter.org) notebook

It is available on all major operating systems (Windows, MacOS, Linux) and requires Python 3.5 or higher.

## Installation

We recommend installing `oommfc` by using either of the `pip` or `conda` package managers.

#### Python requirements

Before installing `oommfc` via `pip`, please make sure you have Python 3.5 or higher on your system. You can check that by running

    python3 --version

If you are on Linux, it is likely that you already have Python installed. However, on MacOS and Windows, this is usually not the case. If you do not have Python 3.5 or higher on your machine, we strongly recommend installing the [Anaconda](https://www.anaconda.com/) Python distribution. [Download Anaconda](https://www.anaconda.com/download) for your operating system and follow instructions on the download page. Further information about installing Anaconda can be found [here](https://conda.io/docs/user-guide/install/download.html).

#### OOMMF requirements

`oommfc` is a Python package used to drive [OOMMF](https://math.nist.gov/oommf/). Therefore, OOMMF is a requirement (dependency) of `oommfc`. If you decide to install `oommfc` using `conda`, then OOMMF will be automatically installed. However, if you decide to use `pip` for `oommfc` installation, we strongly recommend using conda to install OOMMF. You can install OOMMF by running:

    conda install --channel conda-forge oommf
    
**Note:** Details on how to install Anaconda Python distribution can be found in the `conda` section.

#### `pip`

After installing Anaconda on MacOS or Windows, `pip` will also be installed. However, on Linux, if you do not already have `pip`, you can install it with

    sudo apt install python3-pip

To install the `oommfc` version currently in the Python Package Index repository [PyPI](https://pypi.org/project/oommfc/) on all operating systems run:

    python3 -m pip install oommfc

#### `conda`

`oommfc` is installed using `conda` by running

    conda install --channel conda-forge oommfc

For further information on the `conda` package, dependency, and environment management, please have a look at its [documentation](https://conda.io/docs/). 

## Updating

If you used pip to install `oommfc`, you can update to the latest released version in [PyPI](https://pypi.org/project/oommfc/) by running

    python3 -m pip install --upgrade oommfc

On the other hand, if you used `conda` for installation, update `oommfc` with

    conda upgrade oommfc

#### Development version

The most recent development version of `oommfc` that is not yet released can be installed/updated with

    git clone https://github.com/joommf/oommfc
    python3 -m pip install --upgrade oommfc

**Note**: If you do not have `git` on your system, it can be installed by following the instructions [here](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git).

## Binder

`oommfc` can be used in the cloud via Binder. This does not require you to have anything installed and no files will be created on your machine. To use `oommfc` in the cloud, follow this [link](https://mybinder.org/v2/gh/joommf/oommfc/master?filepath=index.ipynb).

## Documentation

Documentation for `oommfc` is available [here](http://oommfc.readthedocs.io/en/latest/?badge=latest), where APIs and tutorials (in the form of Jupyter notebooks) are available.

## Support

If you require support on installation or usage of `oommfc` or if you want to report a problem, you are welcome to raise an issue in our [joommf/help](https://github.com/joommf/help) repository.

## License

Licensed under the BSD 3-Clause "New" or "Revised" License. For details, please refer to the [LICENSE](LICENSE) file.

## How to cite

If you use `oommfc` in your research, please cite it as:

1. M. Beg, R. A. Pepper, and H. Fangohr. User interfaces for computational science: A domain specific language for OOMMF embedded in Python. [AIP Advances, 7, 56025](http://aip.scitation.org/doi/10.1063/1.4977225) (2017).

2. DOI will be available soon

## Acknowledgements

`oommfc` was developed as a part of [OpenDreamKit](http://opendreamkit.org/) – Horizon 2020 European Research Infrastructure project (676541).
