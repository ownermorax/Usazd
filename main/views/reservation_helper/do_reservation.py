from decimal import Decimal

from main.models import Order, Reservation
from main.utils import logger


def do_reservation(
    place_nums,
    profile,
    station_in,
    station_out,
    reservation_date,
    total_price,
    train,
    user,
    repeat="0",
    last_repeat=None,
):
    """Создает бронирование для указанных мест."""

    for place_num in place_nums:
        if Reservation.objects.filter(
            train=train,
            place_num=place_num,
            station_in=station_in,
            station_out=station_out,
            status="active",
        ).exists():
            raise ValueError(f"Место {place_num} уже занято")

    profile.update_balance(-total_price)
    if profile.is_vip:
        cashback = total_price.amount * Decimal("0.05")
        profile.update_balance(cashback)
    profile.save()

    order = Order.objects.create(user=user)

    for place_num in place_nums:
        Reservation.objects.create(
            user=user,
            train=train,
            place_num=place_num,
            station_in=station_in,
            station_out=station_out,
            reservation_date = reservation_date,
            status="active",
            order=order,
            repeat=repeat,
            last_repeat=last_repeat,
        )

    logger.info(f"Успешное бронирование, заказ #{order.id}, мест: {len(place_nums)}.")
    seats_list = ", ".join(place_nums)
    reservation = order.reservations.first()
    return reservation, seats_list
