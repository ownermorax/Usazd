from django.shortcuts import render
from main.models import Train as TrainModel, Profile, Reservation, Station
import json


def train(request):
    """
    Отображает страницу поезда с вагонами и местами.
    """
    train_number = request.GET.get('id', '')
    station_from = request.GET.get('from', '')
    station_to = request.GET.get('to', '')
    carriages_data = []

    train_obj = None
    if train_number:
        all_trains = TrainModel.objects.all()
        for t in all_trains:
            try:
                path_data = json.loads(t.path) if t.path else {}
                if str(path_data.get('number', '')) == str(train_number):
                    train_obj = t
                    break
            except:
                pass

    for carriage_num in range(1, 12):
        seats_data = []
        for seat_num in range(1, 101):
            is_taken = False
            if train_obj:
                place_num = f"{carriage_num}-{seat_num}"
                is_taken = Reservation.objects.filter(
                    train=train_obj,
                    place_num__icontains=place_num,
                    status='active'
                ).exists()

            seats_data.append({
                'number': seat_num,
                'is_taken': is_taken,
            })

        carriages_data.append({
            'number': carriage_num,
            'seats': seats_data,
        })

    context = {
        'carriages': carriages_data,
        'train_number': train_number,
        'station_from': station_from,
        'station_to': station_to,
    }
    return render(request, "train.html", context)