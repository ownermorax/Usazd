# Проект "USAZD"

### Цель

Предоставить пользователю сервис, на котором можно быстро забронировать место в любом поезде.

### Технологический стек:

- Python 3.12
- Django 5.1\+
- SQLite

### Инструкция по настройке проекта:

1. Склонировать проект
2. Открыть проект в PyCharm с наcтройками по умолчанию
3. Создать виртуальное окружение (через settings -\> project "usazd" -\> project interpreter)
Или через консоль:
   ```bash
   python3 -m venv venv

   source venv/bin/activate
   ```
4. Открыть терминал в PyCharm, проверить, что виртуальное окружение активировано.
5. Обновить pip:

   ```bash
   pip install --upgrade pip
   ```
6. Установить в виртуальное окружение необходимые пакеты:

   ```bash
   pip install -r requirements.txt
   ```
7. Синхронизировать структуру базы данных с моделями:

   ```bash
   python manage.py migrate
   ```
8. Получить API яндекс расписаний https://developer.tech.yandex.ru/services и вставить в config.json
9. Запуск:
   ```bash
   python manage.py runserver
   ```