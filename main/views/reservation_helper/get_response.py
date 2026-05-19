from django.http import JsonResponse
from djmoney.money import Money
from main.utils import logger
from .get_attributes import *
from .repetitive_handler import *
from .get_attributes import *
from .get_some_atr import *
from .search_train import *
from .do_reservation import *
from .get_response import *


def get_bad_response(profile, total_price, user_id):
    logger.warning(f"Недостаточно средств у пользователя: #{user_id}.")
    response = JsonResponse(
        {
            "status": "error",
            "message": f"Недостаточно средств. Баланс: ${profile.balance.amount:.2f}, нужно: ${total_price.amount:.2f}",
        },
        status=400,
    )
    return response


def get_last_response(place_nums, profile, reservation, seats_list, total_price):
    response = JsonResponse(
        {
            "status": "success",
            "message": f"Бронирование #{reservation.reservation_id} оформлено! Места: {seats_list}. Сумма: ${total_price.amount:.2f}",
            "reservation_id": reservation.reservation_id,
            "places": place_nums,
            "total_price": str(total_price.amount),
            "new_balance": str(profile.balance.amount),
        },
        status=200,
    )
    return response
