from django.contrib.auth.models import User
from django.shortcuts import render, get_object_or_404
from main.models import Profile
from main.utils import logger


def profile(request, username):
    """
    Отображает страницу профиля пользователя.

    :param request: HTTP запрос
    :type request: HttpRequest

    :param username: имя пользователя из URL
    :type username: str

    :returns: HTTP ответ с шаблоном profile.html
    :rtype: HttpResponse

    """
    user = get_object_or_404(User, username=username)
    logger.info(f"Пользователь {user.username} зашел в профиль.")
    profile, created = Profile.objects.get_or_create(user=user)
    if created:
        logger.info(f"Создан новый профиль для пользователя {user.username}.")
    context = {"user": user, "profile": profile}
    return render(request, "profile.html", context)
