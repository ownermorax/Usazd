from django.shortcuts import render
from main.utils import logger
from main.models import Order


def active_reservations(request):
    """
    Страница с активными бронями пользователя.

    Отображает список текущих активных броней пользователя.

    :param request: HTTP запрос
    :type request: HttpRequest
    :returns: HTTP ответ с шаблоном active_reservations.html
    :rtype: HttpResponse
    """
    orders = Order.objects.filter(user=request.user, status="active").prefetch_related(
        "reservations__train", "reservations__station_in", "reservations__station_out"
    )

    logger.info("Пользователь зашел на страницу с активными бронями пользователя.")
    return render(request, "active_reservations.html", {"orders": orders})
