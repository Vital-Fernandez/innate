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
release = '0.1.8'

# -- Moving documentation building data functions ----------------------------

# import sys
# import os
# import shutil
# from pathlib import Path
#
# def all_but_ipynb(dir, contents):
#     result = []
#     for c in contents:
#         if os.path.isfile(os.path.join(dir, c)) and (not c.endswith(".py")):
#             result += [c]
#     return result
#
#
# _lib_path = Path(__file__).parents[2]/'src'
# _doc_folder = Path(__file__).parents[2]/'docs/source'
# _examples_path = Path(__file__).parents[2]/'examples'
# sys.path.append(_lib_path.as_posix())
# sys.path.append(_examples_path.as_posix())


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

# -- Move the files ------------------------------------------------------------

# shutil.rmtree(_doc_folder/'images', ignore_errors=True)
# shutil.rmtree(_doc_folder/'inputs', ignore_errors=True)
# shutil.rmtree(_doc_folder/'outputs', ignore_errors=True)
# shutil.rmtree(_doc_folder/'sample_data', ignore_errors=True)
# shutil.rmtree(_doc_folder/'tutorials', ignore_errors=True)
# shutil.copytree(_examples_path, _doc_folder, dirs_exist_ok=True)