from djmoney.money import Money
from main.models import Train
import json
from main.utils import logger
from .get_attributes import *
from .repetitive_handler import *
from .get_attributes import *
from .get_some_atr import *
from .search_train import *
from .do_reservation import *
from .get_response import *


def search_train(departure_time, station_in, station_out, train, train_number):
    """Ищет поезд по номеру или создает новый."""
    all_trains = Train.objects.all()
    for t in all_trains:
        try:
            path_data = json.loads(t.path) if t.path else {}
            if str(path_data.get("number", "")) == str(train_number):
                train = t
                break
        except Exception as e:
            logger.warning(f"Ошибка чтения path: {e}.")
    if not train:
        train = Train.objects.create(
            id_station_start=station_in,
            id_station_stop=station_out,
            station_at_time=departure_time or "2024-01-01 00:00:00",
            path=json.dumps({"number": train_number}),
        )
        logger.info(f"Создан новый поезд: #{train.train_id} с номером {train_number}.")
        logger.info(f"Создан новый поезд #{train.train_id} с номером {train_number}")
    return train
