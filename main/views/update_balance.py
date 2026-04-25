from django.shortcuts import render
from main.utils import logger


def update_balance(request):
    """
    Отображает страницу пополнения баланса.

    :param request: Объект HTTP-запроса.
    :type request: HttpRequest
    :returns: HTTP-ответ с шаблоном info.html.
    :rtype: HttpResponse
    """
    logger.info("Пользователь зашел на страницу пополнения баланса.")
    return render(request, 'balance.html')
