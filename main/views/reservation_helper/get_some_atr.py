from djmoney.money import Money

from .do_reservation import *
from .get_attributes import *
from .get_response import *
from .get_some_atr import *
from .repetitive_handler import *
from .search_train import *


def get_some_atr():
    """Возвращает начальные атрибуты для бронирования."""
    booked_seats = []
    place_nums = []
    PRICE_PER_SEAT = Money(2, "USD")
    total_price = Money(0, "USD")
    return PRICE_PER_SEAT, booked_seats, place_nums, total_price
