# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'innate'
copyright = '2024, Vital-Fernandez'
author = 'Vital-Fernandez'
release = '06/25/2024'

# The full version, including alpha/beta/rc tags
release = '0.1.2'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.duration',
    'sphinx.ext.doctest',
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinx.ext.autosummary',
    'sphinx.ext.intersphinx',
    'sphinx.ext.imgmath',
    'matplotlib.sphinxext.plot_directive',
    'sphinx.ext.imgmath',
    'nbsphinx']

templates_path = ['_templates']
exclude_patterns = []

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'alabaster'
html_static_path = ['_static']

html_theme = 'sphinx_rtd_theme'

imgmath_latex_preamble = r'\usepackage[active]{preview}' # + other custom stuff for inline math, such as non-default math fonts etc.
imgmath_use_preview = True