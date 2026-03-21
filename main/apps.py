from django.apps import AppConfig
from main.api_instance import yandex_api
class MainConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'main'
    print(f"станций: {len(yandex_api.stations_id)}")