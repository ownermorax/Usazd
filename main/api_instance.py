from .classes import YandexAPI

yandex_api = YandexAPI()
yandex_api.load_stations_to_json()
yandex_api.load_stations_to_memory()
