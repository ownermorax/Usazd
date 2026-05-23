from .reservation_helper import *
from django.utils import timezone


def reservation_handler(request):
    """Обрабатывает запрос на бронирование мест."""
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
            {"status": "error", "message": "Недостаточно данных для бронирования"},
            status=400,
        )

    if repetitive != "0":
        return repetitive_handler(request)

    try:
        profile = Profile.objects.get(user__id=user_id)
        logger.debug(f"Пользователь найден: #{user_id}.")
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
        logger.error(f"Станции: {station_in} -> {station_out}.")
        train = None
        train = search_train(departure_time, station_in, station_out, train, train_number)
    except Exception as e:
        logger.exception("Ошибка при обработке бронирования.")
        return JsonResponse({"status": "error", "message": f"Ошибка: {str(e)}"}, status=400)
    if departure_time:
        try:
            parsed_time = datetime.fromisoformat(departure_time)
        except BaseException:
            parsed_time = timezone.now()
    else:
        parsed_time = timezone.now()
    PRICE_PER_SEAT, booked_seats, place_nums, total_price = get_some_atr()
    for item in seats.split("W"):
        if item and "x" in item:
            carriage_num = item.split("x")[0]
            seat_num = item.split("x")[1]
            place_num = f"{carriage_num}-{seat_num}"
            if Reservation.objects.filter(train=train, place_num=place_num, status="active").exists():
                logger.warning(f"Место занято: {place_num}.")
                return JsonResponse(
                    {
                        "status": "error",
                        "message": f"Место {seat_num} в вагоне {carriage_num} уже занято",
                    },
                    status=400,
                )
            booked_seats.append({"carriage": carriage_num, "seat": seat_num, "place_num": place_num})
            place_nums.append(place_num)
            total_price += PRICE_PER_SEAT

    if profile.balance < total_price:
        response = get_bad_response(profile, total_price, user_id)
        return response

    reservation, seats_list = do_reservation(place_nums, profile, station_in, station_out, parsed_time, total_price, train, user)
    response = get_last_response(place_nums, profile, reservation, seats_list, total_price)
    return response
