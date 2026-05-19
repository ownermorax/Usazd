from djmoney.money import Money
from main.utils import logger
from .get_attributes import *
from .repetitive_handler import *
from .get_attributes import *
from .get_some_atr import *
from .search_train import *
from .do_reservation import *
from .get_response import *


def get_attributes(request):
    logger.info("Пользователь отправил запрос на бронирование.")
    user_id = request.GET.get("username", "")
    train_number = request.GET.get("train_id", "")
    seats = request.GET.get("seats", "")
    station_in_id = request.GET.get("station_in", "")
    station_out_id = request.GET.get("station_out", "")
    station_in_name = request.GET.get("station_in_name", "")
    station_out_name = request.GET.get("station_out_name", "")
    departure_time = request.GET.get("departure_time", "")
    repetitive = request.GET.get("repetitive", "")
    return (
        departure_time,
        seats,
        station_in_id,
        station_in_name,
        station_out_id,
        station_out_name,
        train_number,
        user_id,
        repetitive,
    )
