from django.apps import AppConfig
from main.api_instance import yandex_api
import threading
import sys
import os

class MainConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'main'
    print(f"станций: {len(yandex_api.stations_id)}")

    def ready(self):
        if 'migrate' in sys.argv or 'makemigrations' in sys.argv:
            return
        if 'shell' in sys.argv:
            return
        if os.environ.get('RUN_MAIN') != 'true':
            return

        def run_parser():
            import time
            time.sleep(2)
            from main.parser import parser
            parser.start()

        thread = threading.Thread(target=run_parser, daemon=True)
        thread.start()
