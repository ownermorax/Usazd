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

8. Получить API яндекс расписаний <https://developer.tech.yandex.ru/services> и вставить в config.json

9. Запуск:

```plaintext
python manage.py runserver
```

# {yellow}(USAZD — деплой с нуля)

**Быстрый старт**

```bash
git clone git@github.com:username/usazd.git /home/dev/usazd
cd /home/dev/usazd
chmod +x deploy.sh
sudo ./deploy.sh
```

---

## Обновление кода

```bash
cd /home/dev/usazd
git pull
sudo systemctl restart gunicorn-usazd
```

---

## Полезные команды


|Команда|Описание|
|:---|:---|
|`sudo systemctl status gunicorn-usazd`|Статус приложения|
|`sudo systemctl restart gunicorn-usazd`|Перезапуск|
|`sudo journalctl -u gunicorn-usazd -f`|Логи в реальном времени|
|`sudo nginx -t && sudo systemctl reload nginx`|Перезагрузка Nginx|
|`sudo certbot renew --dry-run`|Проверка автообновления SSL|

---

## Что внутри [deploy.sh](http://deploy.sh)

1. Установка системных пакетов (nginx, certbot, python)
2. Создание виртуального окружения и установка зависимостей
3. Применение миграций БД
4. Сбор статических файлов
5. Настройка прав доступа
6. Создание systemd-сервиса с `RUN_MAIN=true` (запуск парсеров)
7. Конфигурация Nginx (проксирование на Unix-сокет)
8. Получение SSL-сертификата через Let's Encrypt