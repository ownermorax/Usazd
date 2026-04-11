from django.shortcuts import render
from main.classes import Train


def train(request):
    """
    Отображает страницу поезда с вагонами и местами.

    Создает объект поезда и формирует структуру данных вагонов, мест,
    номер места и статус места (занято/свободно) и передает эти данные в шаблон.

    :param request: HTTP-запрос
    :type request: HttpRequest
    :return: HTTP ответ с шаблоном train.html
    :rtype: HttpResponse
    """

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