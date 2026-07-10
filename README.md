# Проект "USAZD"

### Цель

Предоставить пользователю сервис, на котором можно быстро забронировать место в любом поезде.

### Технологический стек:

- Python 3.12+
- Django 6.0
- SQLite

### Инструкция по настройке проекта:

1. Склонировать проект
2. Создать виртуальное окружение:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. Обновить pip:
   ```bash
   pip install --upgrade pip
   ```
4. Установить зависимости:
   ```bash
   pip install -r requirements.txt
   ```
5. Настроить переменные окружения — скопировать `.env.example` в `.env` и заполнить:
   ```bash
   cp .env.example .env
   ```
   Отредактировать `.env`, указав свои ключи:
   - `SECRET_KEY` — сгенерировать через `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`
   - `YANDEX_API_KEY` — получить на https://developer.tech.yandex.ru/services
   - `OPENROUTER_API_KEY` — получить на https://openrouter.ai/keys (опционально, для нейросети)
6. Синхронизировать базу данных:
   ```bash
   python manage.py migrate
   ```
7. Скачать список станций (требуется YANDEX_API_KEY):
   ```bash
   python download_stations.py
   ```
   Или вручную через API Яндекс.Расписаний.
8. Запуск:
   ```bash
   python manage.py runserver
   ```

### Альтернативный способ настройки API-ключей

Вместо `.env` можно создать файл `main/config.json` (не отслеживается git):
```json
{
    "keys": {
        "YandexAPI": "ваш-ключ-яндекс-расписаний"
    }
}
```
Приоритет имеет переменная окружения `YANDEX_API_KEY`.