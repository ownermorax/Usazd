import os
import sys
import django

# Получаем абсолютный путь к корню репозитория (на один уровень выше папки docs)
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, BASE_DIR)

# Автоматически ищем папку, внутри которой лежит settings.py
settings_module_name = None
for item in os.listdir(BASE_DIR):
    item_path = os.path.join(BASE_DIR, item)
    # Если это папка и внутри неё есть settings.py
    if os.path.isdir(item_path) and os.path.exists(os.path.join(item_path, "settings.py")):
        settings_module_name = f"{item}.settings"
        break

# Если вдруг автоматом не нашли, ставим дефолтный 'main.settings' или 'config.settings'
if not settings_module_name:
    settings_module_name = "main.settings"

# Передаем правильное имя модуля в Django
os.environ["DJANGO_SETTINGS_MODULE"] = settings_module_name

# Запускаем Django
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
