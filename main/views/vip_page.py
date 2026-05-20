from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render

from main.utils import logger


@login_required
def vip(request, username):
    """Отображает VIP страницу пользователя.

    :param request: HTTP запрос
    :param username: Имя пользователя
    :return: HTTP ответ с шаблоном vip.html
    :rtype: HttpResponse
    """
    user = User.objects.get(username=username)
    logger.info("Пользователь зашел на страницу vip.")
    return render(request, "vip.html", {"user": user})
