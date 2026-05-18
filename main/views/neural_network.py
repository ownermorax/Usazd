from django.shortcuts import render


def schedule_card(request, from_station, to_station):
    """Отображает карточку расписания.

    :param request: HTTP запрос
    :param from_station: Станция отправления
    :param to_station: Станция назначения
    :return: HTTP ответ с шаблоном schedule_card.html
    :rtype: HttpResponse
    """
    return render(request, 'main/schedule_card.html', {
        'from_station': from_station,
        'to_station': to_station,
    })


def quick_booking(request):
    """Отображает страницу быстрого бронирования.

    :param request: HTTP запрос
    :return: HTTP ответ с шаблоном quick_booking.html
    :rtype: HttpResponse
    """
    return render(request, 'main/quick_booking.html', {
        'from_station': request.GET.get('from', ''),
        'to_station': request.GET.get('to', ''),
        'date': request.GET.get('date', ''),
    })
