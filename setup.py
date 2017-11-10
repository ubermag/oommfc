import setuptools

with open('README.rst') as f:
    readme = f.read()

setuptools.setup(
    name='oommfc',
    version="0.7.8",
    description='A Python-based OOMMF calculator.',
    long_description=readme,
    url='https://joommf.github.io',
    author='Marijan Beg, Ryan A. Pepper, and Hans Fangohr',
    author_email='jupyteroommf@gmail.com',
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
