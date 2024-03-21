# -*- coding: utf-8 -*-
#
# Configuration file for the Sphinx documentation builder.
#
# This file does only contain a selection of the most common options. For a
# full list see the documentation:
# http://www.sphinx-doc.org/en/master/config

# -- Path setup --------------------------------------------------------------

import os
os.environ["NEXXT_DISABLE_CIMPL"] = "1"  # use pure python version as early as possible
from pathlib import Path
import shutil
import subprocess
import sys
from sphinx.util import logging

logger = logging.getLogger(__name__)

# -- Project information -----------------------------------------------------

project = 'nexxT'
copyright = '2020, ifm electronic gmbh'
author = 'Christoph Wiedemann'

# The short X.Y version
version = ''
# The full version, including alpha/beta/rc tags
release = ''


# -- General configuration ---------------------------------------------------

# If your documentation needs a minimal Sphinx version, state it here.
#
# needs_sphinx = '1.0'

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinxcontrib.apidoc',
    'sphinx.ext.viewcode',
    'breathe', # for c++/doxygen bridge
    'sphinx_rtd_theme',
    'recommonmark',
    'sphinx.ext.autosectionlabel',
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# The suffix(es) of source filenames.
# You can specify multiple suffix as a list of string:
#
#source_suffix = ['.rst', '.md']
source_suffix = '.rst'

# The master toctree document.
master_doc = 'index'

# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
#
# This is also used if you do content translation via gettext catalogs.
# Usually you set "language" from the command line for these cases.
language = 'en'

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store', 'manual']

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = None

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'sphinx_rtd_theme'

# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for each theme, see the
# documentation.
#
html_theme_options = {
    'navigation_depth' : -1, # unlimited depth
    'collapse_navigation' : False,

}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

# see https://rackerlabs.github.io/docs-rackspace/tools/rtd-tables.html
#html_context = {
#    'css_files': [
#        '_static/theme_overrides.css',  # override wide tables in RTD theme
#        ],
#     }

# Custom sidebar templates, must be a dictionary that maps document names
# to template names.
#
# The default sidebars (for documents that don't match any pattern) are
# defined by theme itself.  Builtin themes are using these templates by
# default: ``['localtoc.html', 'relations.html', 'sourcelink.html',
# 'searchbox.html']``.
#
# html_sidebars = {}


# -- Options for HTMLHelp output ---------------------------------------------

# Output file base name for HTML help builder.
htmlhelp_basename = 'nexxTdoc'


# -- Options for LaTeX output ------------------------------------------------

latex_elements = {
    # The paper size ('letterpaper' or 'a4paper').
    #
    # 'papersize': 'letterpaper',

    # The font size ('10pt', '11pt' or '12pt').
    #
    # 'pointsize': '10pt',

    # Additional stuff for the LaTeX preamble.
    #
    # 'preamble': '',

    # Latex figure (float) alignment
    #
    # 'figure_align': 'htbp',
}

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title,
#  author, documentclass [howto, manual, or own class]).
latex_documents = [
    (master_doc, 'nexxT.tex', 'nexxT Documentation',
     'ifm electronic gmbh', 'manual'),
]


# -- Options for manual page output ------------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [
    (master_doc, 'nexxt', 'nexxT Documentation',
     [author], 1)
]


# -- Options for Texinfo output ----------------------------------------------

# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
#  dir menu entry, description, category)
texinfo_documents = [
    (master_doc, 'nexxT', 'nexxT Documentation',
     author, 'nexxT', 'One line description of project.',
     'Miscellaneous'),
]


# -- Options for Epub output -------------------------------------------------

# Bibliographic Dublin Core info.
epub_title = project

# The unique identifier of the text. This can be a ISBN number
# or the project homepage.
#
# epub_identifier = ''

# A unique identification for the text.
#
# epub_uid = ''

# A list of files that should not be packed into the epub file.
epub_exclude_files = ['search.html']


# -- Extension configuration -------------------------------------------------

confpy_dir = os.path.split(os.path.realpath(__file__))[0]

breathe_projects = {
    "nexxT":confpy_dir + "/../c++/xml/",
}

autosectionlabel_prefix_document = True

apidoc_module_dir = confpy_dir + "/../../nexxT"
apidoc_output_dir = "autogenerated"
apidoc_excluded_paths = ["core", "tests"]
apidoc_separate_modules = True
apidoc_toc_file = False
apidoc_module_first = True
#apidoc_extra_args = ["--tocfile", "False"]

# -- Other stuff --

# see https://stackoverflow.com/questions/5599254/how-to-use-sphinxs-autodoc-to-document-a-classs-init-self-method
def skip(app, what, name, obj, would_skip, options):
    if name == "__init__":
        # always include constructors
        return False
    if name in ["CONSTRUCTING",
                "CONSTRUCTED",
                "INITIALIZING",
                "INITIALIZED",
                "OPENING",
                "OPENED",
                "STARTING",
                "ACTIVE",
                "STOPPING",
                "CLOSING",
                "DEINITIALIZING",
                "DESTRUCTING",
                "DESTRUCTED"]:
        # skip the state machine entries
        return True
    if name == "Services":
        if not hasattr(skip, "srvseen"):
            skip.srvseen = set()
        if obj in skip.srvseen:
            return True
        skip.srvseen.add(obj)
    return would_skip

def remove_apidoc_artifacts(app):
    if not hasattr(remove_apidoc_artifacts, "done"):
        logger.info("Remove the autogenerated nexxT.rst file in favour of the overwritten version")
        os.remove(confpy_dir + "/autogenerated/nexxT.rst")
        remove_apidoc_artifacts.done = True

def setup(app):
    app.connect("autodoc-skip-member", skip)
    app.connect("builder-inited", remove_apidoc_artifacts)
    app.add_css_file('theme_overrides.css')
    shutil.rmtree(confpy_dir + "/autogenerated", ignore_errors=True)
    shutil.rmtree(confpy_dir + "/../c++/xml", ignore_errors=True)
    os.makedirs(confpy_dir + "/autogenerated", exist_ok=True)
    with open(confpy_dir + "/autogenerated/nexxT-gui.txt", "wb") as f:
        f.write(subprocess.check_output([os.path.split(sys.executable)[0] + "/nexxT-gui", "--help"]))
    with open(confpy_dir + "/autogenerated/nexxT-console.txt", "wb") as f:
        f.write(subprocess.check_output([os.path.split(sys.executable)[0] + "/nexxT-console", "--help"]))
    with open(confpy_dir + "/autogenerated/introduction.md", "w") as f:
        f.writelines(
            ["# Introduction\n", "\n"] +
            list(open(confpy_dir + "/../../README.md", "r").readlines())[2:]
        )
    subprocess.check_call("doxygen", cwd=confpy_dir + "/../c++")
    logger.info("Directory listing of #/doc:")
    for p in (Path(confpy_dir) / "..").rglob("**/*"):
        logger.info("  %s", str(p))
    logger.info("pip freeze output")
    logger.info(subprocess.check_output([sys.executable, "-m", "pip", "freeze"]).decode())
