#!/usr/bin/env python3
"""Скрипт для загрузки stations.json из API Яндекс.Расписаний.

Требует установленной переменной окружения YANDEX_API_KEY или файла config.json.
"""
import json
import os
import sys

import requests


def main():
    api_key = os.environ.get("YANDEX_API_KEY")
    if not api_key:
        try:
            with open("main/config.json") as f:
                conf = json.load(f)
                api_key = conf["keys"]["YandexAPI"]
        except (FileNotFoundError, KeyError):
            print("Ошибка: не задан YANDEX_API_KEY и не найден config.json")
            sys.exit(1)

    print("Загрузка списка станций...")
    response = requests.get(
        f"https://api.rasp.yandex-net.ru/v3.0/stations_list/?apikey={api_key}&lang=ru_RU&format=json",
        timeout=120,
    )
    response.raise_for_status()

    with open("stations.json", "w", encoding="utf-8") as f:
        json.dump(response.json(), f, ensure_ascii=False, indent=4)

    print("Список станций сохранён в stations.json")


if __name__ == "__main__":
    main()