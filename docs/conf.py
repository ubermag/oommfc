# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
# import os
# import sys
# sys.path.insert(0, os.path.abspath('.'))


# -- Project information -----------------------------------------------------

project = 'oommfc'
copyright = '2021, Marijan Beg and Hans Fangohr'
author = ('Marijan Beg, Martin Lang, Ryan A. Pepper, '
          'Thomas Kluyver, and Hans Fangohr')


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.napoleon',
    'sphinx.ext.mathjax',
    'nbsphinx',
    'm2r2'
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'sphinx_rtd_theme'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
# html_static_path = ['_static']

# Custom configuration
autosummary_generate = True
autosummary_imported_members = True
autosummary_context = {
    'excluded_members': ['__radd__', '__rand__', '__rlshift__', '__rmatmul__',
                         '__rmul__', '__rsub__', '__rtruediv__', '__delattr__',
                         '__format__', '__ge__', '__getattribute__', '__gt__',
                         '__init__', '__init_subclass__', '__le__', '__lt__',
                         '__ne__', '__new__', '__reduce__', '__reduce_ex__',
                         '__setattr__', '__sizeof__', '__str__', '__eq__',
                         '__subclasshook__', '__hash__', '__dir__', '__repr__',
                         '__iter__']
}

autoclass_content = 'class'
autodoc_inherit_docstrigs = True
autodoc_default_options = {
    'member-order': 'groupwise',
    'exclude-members': '__init__, __weakref__'
}
