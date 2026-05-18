# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys
import django

# Получаем абсолютный путь к папке docs/
DOCS_DIR = os.path.dirname(os.path.abspath(__file__))

# Получаем абсолютный путь к корню проекта (на один уровень выше docs/)
BASE_DIR = os.path.dirname(DOCS_DIR)

# Принудительно добавляем корень проекта в самое начало путей поиска Python
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# Задаем переменную окружения для настроек Django
os.environ["DJANGO_SETTINGS_MODULE"] = "usazd.settings"

# Инициализируем Django
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
