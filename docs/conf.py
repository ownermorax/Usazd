import os
import sys
import django

# 1. Получаем абсолютный путь к корню репозитория
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, BASE_DIR)

# 2. ИСПРАВЛЕНИЕ: Меняем рабочую директорию процесса на корень,
# чтобы сработал `with open('main/config.json')`
os.chdir(BASE_DIR)

# 3. Автоматически ищем папку, внутри которой лежит settings.py
settings_module_name = None
for item in os.listdir(BASE_DIR):
    item_path = os.path.join(BASE_DIR, item)
    if os.path.isdir(item_path) and os.path.exists(os.path.join(item_path, "settings.py")):
        settings_module_name = f"{item}.settings"
        break

if not settings_module_name:
    settings_module_name = "main.settings"

# 4. Передаем настройки и стартуем
os.environ["DJANGO_SETTINGS_MODULE"] = settings_module_name
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
