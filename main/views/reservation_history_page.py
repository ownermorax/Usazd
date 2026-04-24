from django.shortcuts import render
from main.utils import logger


def reservation_history(request):
    """
    Страница с историей броней пользователя.

    Отображает список завершенных броней пользователя.

    :param request: HTTP запрос
    :type request: HttpRequest
    :returns: HTTP ответ с шаблоном reservation_history.html
    :rtype: HttpResponse
    """
    logger.info("Пользователь зашел на страницу с историей брони.")
    return render(request, 'reservation_history.html')