# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys
import django

# ИСПРАВЛЕНО: Корень проекта находится на ОДИН уровень выше папки docs/
sys.path.insert(0, os.path.abspath(".."))

# ДОБАВЛЕНО: Указываем Django, где искать настройки, и инициализируем его
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "usazd.settings") # Замени usazd на имя папки, если нужно
django.setup()

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

autodoc_default_options = {"members": True, "undoc-members": True}

project = "usazd"
copyright = "2026, Ы, Agniya, dark7es, goose.pm, Most, Morax, marysh"
author = "Ы, Agniya, dark7es, goose.pm, Most, Morax, marysh"
release = "27.03.26"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ["sphinx.ext.autodoc"]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "alabaster"
html_static_path = ["_static"]
