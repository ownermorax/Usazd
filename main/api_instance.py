"""Модуль для создания экземпляра API Яндекс.Расписания.

Создает глобальный экземпляр YandexAPI и загружает данные станций.
"""

from .classes import YandexAPI

yandex_api = YandexAPI()
yandex_api.load_stations_to_json()
yandex_api.load_stations_to_memory()
