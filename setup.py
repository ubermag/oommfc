import setuptools

with open('README.rst') as f:
    readme = f.read()

setuptools.setup(
    name='oommfc',
    version='0.5.4.3',
    description='A Python-based OOMMF calculator.',
    long_description=readme,
    url='https://github.com/joommf/oommfc',
    author='Computational Modelling Group',
    author_email='fangohr@soton.ac.uk',
    packages=setuptools.find_packages(),
    install_requires=['scipy',
                      'discretisedfield',
                      'micromagneticmodel',
                      'oommfodt'],
    classifiers=['Development Status :: 3 - Alpha',
                 'License :: OSI Approved :: BSD License',
                 'Topic :: Scientific/Engineering :: Physics',
                 'Intended Audience :: Science/Research',
                 'Programming Language :: Python :: 3 :: Only']
)
