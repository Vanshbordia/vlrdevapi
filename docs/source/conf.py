import os
import sys
import importlib.metadata as _metadata
sys.path.insert(0, os.path.abspath('../../src'))

project = 'vlrdevapi'
copyright = '2025, Vansh'
author = 'Vansh'

# The full version, including alpha/beta/rc tags
try:
    release = _metadata.version("vlrdevapi")
except _metadata.PackageNotFoundError:
    release = "1.6.1"

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.autodoc.typehints',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
    'sphinx.ext.intersphinx',
    'sphinx.ext.autosummary',
    'sphinx_copybutton',
]

autodoc_default_options = {
    'members': True,
    'member-order': 'bysource',
    'special-members': '__init__',
    'undoc-members': True,
    'exclude-members': '__weakref__'
}

autosummary_generate = True
napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = True

templates_path = ['_templates']
exclude_patterns = []

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

html_theme_options = {
    'navigation_depth': 4,
    'collapse_navigation': False,
    'sticky_navigation': True,
    'includehidden': True,
    'titles_only': False
}

intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
}
