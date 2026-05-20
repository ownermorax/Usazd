import os
import sys
import threading

from django.apps import AppConfig

from main.api_instance import yandex_api
from main.utils import logger


class MainConfig(AppConfig):
    """Конфигурация приложения main.

    Инициализирует приложение и запускает фоновые процессы для парсинга.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "main"
    print(f"станций: {len(yandex_api.stations_id)}")

    def ready(self):
        """Выполняется при готовности приложения.

        Запускает фоновые потоки для парсинга USDT транзакций и проверки VIP статусов.
        """
        if "migrate" in sys.argv or "makemigrations" in sys.argv:
            return
        if "shell" in sys.argv:
            return
        if os.environ.get("RUN_MAIN") != "true":
            return

        def run_usdt_parser():
            """Запускает парсер USDT транзакций в фоновом режиме."""
            import time

            time.sleep(2)
            from main.parser import parser

            parser.start_parser("usdt")

            parser.start()

        def run_premium_parser():
            """Запускает проверку истечения VIP статусов в фоновом режиме."""
            import time

            time.sleep(3)
            from main.parser import parser

            parser.start_parser("vip")

        def run_resrvation_parser():
            """Запускает проверку на повторные бронирования в фоновом режиме."""
            import time

            time.sleep(4)
            from main.parser import parser

            parser.start_parser("reservation")

        thread_usdt = threading.Thread(target=run_usdt_parser, daemon=True)
        thread_usdt.start()
        logger.info(f"USDT парсер запущен")

        thread_premium = threading.Thread(target=run_premium_parser, daemon=True)
        thread_premium.start()
        logger.info(f"VIP парсер запущен")

        thread_premium = threading.Thread(target=run_resrvation_parser, daemon=True)
        thread_premium.start()
        logger.info(f"Reservation парсер запущен")
