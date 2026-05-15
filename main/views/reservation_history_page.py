from django.shortcuts import render
from main.utils import logger
from main.models import Reservation



def reservation_history(request):
    """
    Страница с историей броней пользователя.

    Отображает список завершенных броней пользователя.

    :param request: HTTP запрос
    :type request: HttpRequest
    :returns: HTTP ответ с шаблоном reservation_history.html
    :rtype: HttpResponse
    """
    reservations = Reservation.objects.filter(user=request.user, status__in=['cancelled', 'completed']).select_related('train', 'station_in', 'station_out')
    logger.info("Пользователь зашел на страницу с историей брони.")
    return render(request, 'reservation_history.html', {'reservations': reservations})