from django.shortcuts import render
from main.classes import Train


def train(request):#TODO: переделать docstring коментарий
    """Функция для отображения страницы поезда"""

    train = Train()
    carriages_data = []
    for carriage in train.carriages:
        seats_data = []
        for seats in carriage.seats:
            seats_data.append({
                'number': seats.number,
                'is_taken': seats.is_taken,
            })


        carriages_data.append({
            'number': carriage.number,
            'seats': seats_data,
        })

    context = {
            'train': train,
            'carriages': carriages_data,
    }
    return render(request, "train.html", context)