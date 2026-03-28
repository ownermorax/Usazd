Установка
=========

Требования
----------
- Python 3.8+
- Django 4.x
- Другие зависимости (указаны в requirements.txt)

Клонирование репозитория
------------------------
.. code-block:: bash

    git clone <your-repo-url>
    cd usazd

Настройка виртуального окружения
--------------------------------
.. code-block:: bash

    python -m venv venv
    source venv/bin/activate

Установка зависимостей
----------------------
.. code-block:: bash

    pip install -r requirements.txt

Настройка базы данных
---------------------
.. code-block:: bash

    python manage.py migrate
    python manage.py createsuperuser

Запуск сервера
--------------
.. code-block:: bash

    python manage.py runserver

Приложение будет доступно по адресу: http://127.0.0.1:8000