from django.shortcuts import render
from main.utils import logger
from main.models import Order


def reservation_history(request):
    """
    Страница с историей броней пользователя.

    Отображает список завершенных броней пользователя.

    :param request: HTTP запрос
    :type request: HttpRequest
    :returns: HTTP ответ с шаблоном reservation_history.html
    :rtype: HttpResponse
    """
    orders = Order.objects.filter(
        user=request.user,
        status__in=["cancelled", "completed"]
    ).prefetch_related("reservations__train", "reservations__station_in", "reservations__station_out")

    logger.info("Пользователь зашел на страницу с историей брони.")
    return render(request, "reservation_history.html", {"orders": orders})