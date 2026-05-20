from django.shortcuts import render
from main.models import Train as TrainModel, Profile, Reservation, Station
import json
from main.utils import logger


def train(request):
    """Отображает страницу поезда с вагонами и местами."""
    train_number = request.GET.get("id", "")
    logger.info(f"Пользователь зашел на страницу поезда: {train_number}.")
    station_from = request.GET.get("from", "")
    station_to = request.GET.get("to", "")
    departure_time = request.GET.get("departure_time", "")
    carriages_data = []

    train_obj = None
    train_obj = find_train(train_number, train_obj)

    reserved_places = set()
    if train_obj:
        reservations = Reservation.objects.filter(train=train_obj, status="active")
        for res in reservations:
            places = res.place_num.split(", ")
            for place in places:
                reserved_places.add(place.strip())

    for carriage_num in range(1, 12):
        seats_data = []
        for seat_num in range(1, 101):
            place_num = f"{carriage_num}-{seat_num}"
            is_taken = place_num in reserved_places

            seats_data.append(
                {
                    "number": seat_num,
                    "is_taken": is_taken,
                }
            )

        carriages_data.append(
            {
                "number": carriage_num,
                "seats": seats_data,
            }
        )

    context = {
        "carriages": carriages_data,
        "train_number": train_number,
        "station_from": station_from,
        "station_to": station_to,
        "departure_time": departure_time,
    }
    return render(request, "train.html", context)


def find_train(train_number, train_obj):
    """Находит поезд по номеру или создает новый."""
    if train_number:
        all_trains = TrainModel.objects.all()
        for t in all_trains:
            try:
                path_data = json.loads(t.path) if t.path else {}
                if str(path_data.get("number", "")) == str(train_number):
                    train_obj = t
                    break
            except Exception as e:
                logger.warning(f"Ошибка path: {e}.")
        logger.debug(f"Поезд найден: {bool(train_obj)}.")
    return train_obj
