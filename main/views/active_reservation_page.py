from django.shortcuts import render
from main.utils import logger


def active_reservations(request):
    """
    Страница с активными бронями пользователя.

    Отображает список текущих активных броней пользователя.

    :param request: HTTP запрос
    :type request: HttpRequest
    :returns: HTTP ответ с шаблоном active_reservations.html
    :rtype: HttpResponse
    """
    logger.info("Пользователь зашел на страницу с активными бронями пользователя.")
    return render(request, 'active_reservations.html')
