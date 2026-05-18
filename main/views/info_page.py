from django.shortcuts import render
from main.utils import logger


def info(request):
    """
    Отображает информационную страницу.

    :param request: Объект HTTP-запроса.
    :type request: HttpRequest
    :returns: HTTP-ответ с шаблоном info.html.
    :rtype: HttpResponse
    """
    logger.info("Пользователь зашел на информационную страницу.")
    return render(request, "info.html")
