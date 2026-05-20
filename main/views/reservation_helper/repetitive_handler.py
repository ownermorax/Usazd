from typing import Any

from django.http import JsonResponse
from main.models import Profile, Station, Reservation, Train
from datetime import datetime
from django.utils import timezone
from djmoney.money import Money
from main.utils import logger
from datetime import timedelta


def repetitive_handler(request):
    from .get_attributes import get_attributes
    from .do_reservation import do_reservation

    (
        departure_time,
        seats,
        station_in_id,
        station_in_name,
        station_out_id,
        station_out_name,
        train_number,
        user_id,
        repetitive,
    ) = get_attributes(request)

    if not user_id or not train_number or not seats:
        return JsonResponse(
            {
                "status": "error",
                "message": "Недостаточно данных для повторяющегося бронирования",
            },
            status=400,
        )

    try:
        profile = Profile.objects.get(user__id=user_id)
        user = profile.user

        if station_in_id:
            station_in = Station.objects.get(station_id=station_in_id)
        elif station_in_name:
            station_in, _ = Station.objects.get_or_create(name=station_in_name)
        else:
            return JsonResponse(
                {"status": "error", "message": "Не указана станция отправления"},
                status=400,
            )

        if station_out_id:
            station_out = Station.objects.get(station_id=station_out_id)
        elif station_out_name:
            station_out, _ = Station.objects.get_or_create(name=station_out_name)
        else:
            return JsonResponse(
                {"status": "error", "message": "Не указана станция назначения"},
                status=400,
            )

        parsed_time, place_nums, repeat_hours, total_price, train = get_some_atr(
            departure_time, repetitive, seats, station_in, station_out, train_number
        )

        if profile.balance < total_price:
            return JsonResponse(
                {
                    "status": "error",
                    "message": f"Недостаточно средств для повторяющегося бронирования",
                },
                status=400,
            )

        reservation, seats_list = do_reservation(
            place_nums,
            profile,
            station_in,
            station_out,
            total_price,
            train,
            user,
            repeat_hours,
            parsed_time,
        )

        logger.info(
            f"Повторяющееся бронирование #{reservation.reservation_id} создано для пользователя #{user_id}"
        )

        return JsonResponse(
            {
                "status": "success",
                "message": f"Повторяющееся бронирование #{reservation.reservation_id} создано",
                "reservation_id": reservation.reservation_id,
            },
            status=200,
        )

    except Exception as e:
        logger.exception("Ошибка при создании повторяющегося бронирования")
        return JsonResponse(
            {"status": "error", "message": f"Ошибка: {str(e)}"}, status=400
        )


def get_some_atr(
    departure_time,
    repetitive,
    seats,
    station_in: Station,
    station_out: Station,
    train_number,
) -> tuple[Any, list[Any], Train | Any, str, datetime]:
    from .search_train import search_train

    train = None
    train = search_train(departure_time, station_in, station_out, train, train_number)

    place_nums = []
    for item in seats.split("W"):
        if item and "x" in item:
            carriage_num = item.split("x")[0]
            seat_num = item.split("x")[1]
            place_num = f"{carriage_num}-{seat_num}"
            place_nums.append(place_num)

    if departure_time:
        try:
            parsed_time = datetime.fromisoformat(departure_time)
        except:
            parsed_time = timezone.now()
    else:
        parsed_time = timezone.now()

    repetitive_int = int(repetitive)
    if repetitive_int == 1:
        repeat_hours = "24"
    elif repetitive_int == 2:
        repeat_hours = "168"
    else:
        repeat_hours = "0"

    total_price = Money(len(place_nums) * 2, "USD")
    return parsed_time, place_nums, repeat_hours, total_price, train


def add_repetitive_reservation(reservation):
    from .do_reservation import do_reservation
    profile = Profile.objects.get(user=reservation.user)
    places = reservation.place_num.split(", ")
    total_price = Money(len(places) * 2, "USD")

    if profile.balance >= total_price:
        repeat_hours = int(reservation.repeat)
        new_departure_time = reservation.last_repeat + timedelta(hours=repeat_hours)

        new_reservation, seats_list = do_reservation(
            places, profile, reservation.station_in, reservation.station_out,
            total_price, reservation.train, reservation.user, reservation.repeat, new_departure_time
        )

        reservation.repeat = "0"
        reservation.save()

        logger.info(
            f"Повторяющаяся бронь #{reservation.reservation_id}: создана новая резервация на {new_departure_time}")
        return True
    else:
        logger.warning(f"Повторяющаяся бронь #{reservation.reservation_id}: недостаточно средств")
        return False