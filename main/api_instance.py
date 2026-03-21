from main.classes import YandexAPI

yandex_api = YandexAPI()
yandex_api.load_stations_to_memory()
print(f" Загружено {len(yandex_api.stations_id)} станций")